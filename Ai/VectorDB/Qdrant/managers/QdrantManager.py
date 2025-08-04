from qdrant_client.http.models import VectorParams
from typing import List, Optional
from qdrant_client.http.models import PointStruct, PointIdsList
import logfire
from qdrant_client import QdrantClient,AsyncQdrantClient

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