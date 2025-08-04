from fastapi import HTTPException, Depends, FastAPI, Request
from typing import List, Optional
import json
import uuid
import logfire
import asyncio

from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct, PointIdsList
from sentence_transformers import SentenceTransformer

from Qdrant.schemas import TableCreate, Table, Column, ColumnCreate, TableResponse

# Domain layer
class QdrantManager:
    def __init__(self, client: AsyncQdrantClient):
        self.client = client

    async def create_collection(self, name: str, vectors_config: VectorParams):
        try:
            await self.client.create_collection(
                collection_name=name, 
                vectors_config=vectors_config
            )
            logfire.info(f"Collection {name} created successfully.")
        except Exception as e:
            logfire.error(f"Failed to create collection {name}: {str(e)}")
            raise

    async def delete_collection(self, name: str):
        try:
            await self.client.delete_collection(collection_name=name)
            logfire.info(f"Collection {name} deleted successfully.")
        except Exception as e:
            logfire.error(f"Failed to delete collection {name}: {str(e)}")
            raise

    async def get_collection(self, name: str):
        try:
            collection = await self.client.get_collection(name)
            logfire.info(f"Collection {name} retrieved successfully.")
            return collection
        except Exception as e:
            logfire.error(f"Failed to get collection {name}: {str(e)}")
            raise

    async def add_points(self, name: str, points: List[PointStruct]):
        try:
            # Check if the collection exists.
            try:
                await self.client.get_collection(name)
            except Exception:
                # If the collection doesn't exist, create it with default vector parameters.
                default_vectors_config = VectorParams(size=384, distance="Cosine")
                await self.client.create_collection(
                    collection_name=name, 
                    vectors_config=default_vectors_config
                )
                logfire.info(f"Collection {name} created with default vector parameters.")
            # Upsert the points into the collection.
            await self.client.upsert(
                collection_name=name,
                wait=True,
                points=points
            )
            logfire.info(f"Points added to collection {name} successfully.")
        except Exception as e:
            logfire.error(f"Failed to add points to collection {name}: {str(e)}")
            raise

    async def get_point_by_id(self, collection_name: str, point_id: int):
        try:
            point = await self.client.retrieve(
                collection_name=collection_name,
                ids=[point_id]
            )
            
            logfire.info(f"Point {point_id} retrieved from collection {collection_name} successfully.")
            return point
        except Exception as e:
            logfire.error(f"Failed to get point by ID {point_id} from collection {collection_name}: {str(e)}")
            raise

    async def search(self, name: str, query: List[float], limit: int):
        try:
            # Execute the search and include the payload in the results
            result = await self.client.query_points(
                collection_name=name,
                query=query,
                limit=limit,
                with_payload=True  # Retrieve full payload
            )
            logfire.info(f"Search in collection {name} executed successfully.")
            return result
        except Exception as e:
            logfire.error(f"Failed to search in collection {name}: {str(e)}")
            return []

    async def update_point(
        self, 
        collection_name: str, 
        point_id: int, 
        new_vector: Optional[List[float]] = None, 
        new_payload: Optional[dict] = None
    ):
        try:
            # First, retrieve the existing point
            existing = await self.get_point_by_id(collection_name, point_id)
            if not existing or len(existing) == 0:
                raise Exception(f"Point with ID {point_id} not found in collection {collection_name}")
            
            # Use new values if provided; otherwise use existing data.
            updated_vector = new_vector if new_vector is not None else existing.vector
            updated_payload = new_payload if new_payload is not None else existing.payload
            
            updated_point = PointStruct(
                id=point_id,
                vector=updated_vector,
                payload=updated_payload
            )
            
            await self.client.upsert(
                collection_name=collection_name,
                wait=True,
                points=[updated_point]
            )
            logfire.info(f"Point {point_id} updated in collection {collection_name} successfully.")
            
            return await self.get_point_by_id(collection_name, point_id)
        except Exception as e:
            logfire.error(f"Failed to update point {point_id} in collection {collection_name}: {str(e)}")
            raise

    async def point_delete(self, collection_name: str, point_ids: List[str]):
        try:
            await self.client.delete(
                collection_name=collection_name,
                points_selector=PointIdsList(points=point_ids)
            )
            logfire.info(f"Points {point_ids} deleted from collection {collection_name} successfully.")
        except Exception as e:
            logfire.error(f"Failed to delete points {point_ids} from collection {collection_name}: {str(e)}")
            print("error :", e)
            raise

    async def get_all_points(self, collection_name: str):
        try:
            points = []
            next_offset = None
            while True:
                # Await the scroll operation for the next batch of points
                points_batch, next_offset = await self.client.scroll(
                    collection_name=collection_name,
                    scroll_filter=None,
                    limit=100,
                    offset=next_offset
                )
                points.extend(points_batch)
                if next_offset is None:
                    break
            logfire.info(f"All points retrieved from collection {collection_name} successfully.")
            return points
        except Exception as e:
            logfire.error(f"Failed to get all points from collection {collection_name}: {str(e)}")
            raise

async def get_client(request: Request) -> AsyncQdrantClient:
    """Dependency to get the shared Qdrant client"""
    return request.app.state.qdrant_client

class Embeddings:
    def __init__(self, model_id: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the embedding model.
        """
        logfire.info(f"Initializing Embedding model with ID: {model_id}")
        self.embedding_model = SentenceTransformer(model_id)
    
    async def embed_docs(self, documents: List[dict]) -> List[PointStruct]:
        """
        For each document, generate an embedding for its 'content' asynchronously
        and create a PointStruct with the embedding and the document payload.
        
        Args:
            documents (List[dict]): A list of documents, each having at least 'id', 'content', and 'payload' keys.
            
        Returns:
            List[PointStruct]: A list of Qdrant PointStruct objects.
        """
        logfire.info(f"Embedding {len(documents)} documents")
        points = []
        for doc in documents:
            try:
                # Offload the blocking embedding call to a thread.
                embedding_vector = await asyncio.to_thread(self.embedding_model.encode, doc["content"])
                point = PointStruct(
                    id=doc["id"],
                    vector=embedding_vector,
                    payload=doc["payload"]
                )
                points.append(point)
                logfire.info(f"Embedded {len(points)} points so far")
            except Exception as e:
                logfire.exception(f"Failed to embed document: {str(e)}")
        return points

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate an embedding for the given text asynchronously.
        
        Args:
            text (str): The text to embed.
            
        Returns:
            List[float]: The embedding vector for the text.
        """
        return await asyncio.to_thread(self.embedding_model.encode, text)


class QdrantService:
    def __init__(self ,client: AsyncQdrantClient = Depends(get_client)):
        logfire.info("Qdrant Service initialized")
        self.__manager = QdrantManager(client)
        self.__embeddings = Embeddings()

    async def create_collection(self, name: str, vectors_config: VectorParams = VectorParams(size=384, distance=Distance.DOT)):
        await self.__manager.create_collection(name, vectors_config)

    async def add_points(self, name: str, docs: List[dict]):
        logfire.info("Adding points to Qdrant")
        points = await self.__embeddings.embed_docs(docs)
        await self.__manager.add_points(name, points)

    async def get_point(self, collection_name: str, point_id: str):
        point = await self.__manager.get_point_by_id(collection_name, point_id)
        return point

    async def get_all_points(self, collection_name: str):
        return await self.__manager.get_all_points(collection_name)

    async def search(self, name: str, query: str, limit: int):
        query = await self.__embeddings.embed_text(query)
        return await self.__manager.search(name, query, limit)

    async def update_point(self, collection_name: str, point_id: str, newdoc: dict):
        try:
            new_vector = await self.__embeddings.embed_text(newdoc['content'])
            new_payload = newdoc['payload']
            await self.__manager.update_point(collection_name, point_id, new_vector, new_payload)
        except RuntimeError:
            return "Failed to update point"

    async def delete_point(self, collection_name: str, point_id: str):
        await self.__manager.point_delete(collection_name, [point_id])


class TableService:
    """
    Service for managing table records in Qdrant.
    """
    def __init__(self, collection_name: str = "tables_collection",qdrant_service: QdrantService = Depends()):
        with logfire.span("TableService"):
            self.__qdrant_service = qdrant_service
            self.__collection_name = collection_name

    async def create_table(self, table: TableCreate) -> TableResponse:
        try:
            logfire.info("Creating table in Qdrant")
            generated_table_id = str(uuid.uuid4())
            # Generate column IDs for each column
            columns_with_id = [
                Column(
                    id=str(uuid.uuid4()),
                    name=col.name,
                    alias=col.alias,
                    description=col.description,
                    data_type=col.data_type,
                    is_nullable=col.is_nullable,
                    is_primary_key=col.is_primary_key,
                    is_foreign_key=col.is_foreign_key,
                    foreign_key_table_id=col.foreign_key_table_id,
                    is_unique=col.is_unique,
                    is_indexable=col.is_indexable,
                    is_searchable=col.is_searchable,
                    is_filterable=col.is_filterable,
                )
                for col in table.columns
            ]
            
            table_json = {
                "id": generated_table_id,
                "content": json.dumps(table.model_dump()),
                "payload": table.model_dump()
            }
            # Await the asynchronous upsert/add operation
            await self.__qdrant_service.add_points(self.__collection_name, [table_json])
            logfire.info("Table created successfully in Qdrant")
            return TableResponse(
                id=generated_table_id,
                name=table.name,
                alias=table.alias,
                description=table.description,
                columns=columns_with_id
            )
        except Exception as e:
            logfire.error(f"Failed to create table: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create table: {str(e)}")

    async def get_table(self, table_id: int):
        try:
            result = await self.__qdrant_service.get_point(self.__collection_name, table_id)
            if not result:
                raise HTTPException(status_code=404, detail="Table not found")
            return result[0].payload
        except Exception as e:
            logfire.error(f"Error retrieving table: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error retrieving table: {str(e)}")

    async def get_tables(self) -> List[Optional[TableResponse]]:
        try:
            tables = await self.__qdrant_service.get_all_points(self.__collection_name)
            table_responses = [table.payload for table in tables]
            return table_responses
        except Exception as e:
            logfire.error(f"Error retrieving tables: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error retrieving tables: {str(e)}")

    async def delete_table(self, table_id: str):
        try:
            await self.__qdrant_service.delete_point(self.__collection_name, table_id)
        except Exception as e:
            error_msg = str(e).lower()
            if "not found" in error_msg:
                raise HTTPException(status_code=400, detail="Table does not exist")
            else:
                raise HTTPException(status_code=500, detail=f"Failed to delete table: {str(e)}")
        
    async def update_table(self, table_id: str, table: TableCreate) -> TableResponse:
        try:
            updated_table_json = {
                "id": table_id,
                "content": json.dumps(table.model_dump()),
                "payload": table.model_dump()
            }
            updated = await self.__qdrant_service.update_point(
                self.__collection_name, table_id, updated_table_json
            )
            if not updated:
                raise HTTPException(status_code=404, detail="Table not found")
            return updated
        except Exception as e:
            error_msg = str(e).lower()
            if "not found" in error_msg:
                raise HTTPException(status_code=400, detail="Table does not exist")
            else:
                raise HTTPException(status_code=500, detail=f"Failed to update table: {str(e)}")


class SearchService:
    def __init__(self, collection_name: str = "tables_collection",qdrant_service: QdrantService = Depends()):
        self.__qdrant_service = qdrant_service
        self.__collection_name = collection_name
        
    async def search(self, query: str, limit: int):
        logfire.info(f"Searching in Qdrant for query: {query}")
        try:
            result = await self.__qdrant_service.search(self.__collection_name, query, limit)
            return result
        except Exception as e:
            logfire.error(f"Error during search: {str(e)}")
            raise e