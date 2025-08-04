from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import VectorParams, Distance
from Qdrant.managers.QdrantManager import QdrantManager
from typing import List
from qdrant_client.http.models import PointStruct
from Qdrant.embeddings import Embeddings
from Qdrant.schemas import TableCreate, Table, Column, ColumnCreate, TableResponse
import json
import uuid
import logfire
from fastapi import FastAPI, Depends
from Qdrant.db import get_client
from Qdrant.managers.QdrantManager import QdrantManager

class QdrantService:
    def __init__(self, client: AsyncQdrantClient = Depends(get_client)):
        with logfire.span("Initialize QdrantService") as span:
            span.set_attributes({
                "client_config": client
            })
            print("This is the Span:",span)
            self.__manager = QdrantManager(client)
            self.__embeddings = Embeddings()
            logfire.info("Service initialized", result=self)

    async def create_collection(self, name: str, vectors_config: VectorParams = VectorParams(size=384, distance=Distance.DOT)):
        with logfire.span("CreateCollection") as span:
            span.set_attributes({
                "collection_name": name,
                "vector_size": vectors_config.size,
                "distance_metric": vectors_config.distance.value
            })
            await self.__manager.create_collection(name, vectors_config)
            logfire.info("Collection created successfully")

    async def add_points(self, name: str, docs: List[dict]):
        with logfire.span("AddPoints") as span:
            span.set_attributes({
                "collection_name": name,
                "document_count": len(docs)
            })
            with logfire.span("EmbedDocuments"):
                points = await self.__embeddings.embed_docs(docs)
                span.set_attribute("points_generated", len(points))
            
            with logfire.span("QdrantInsert"):
                await self.__manager.add_points(name, points)
            
            logfire.info("Points added successfully", 
                        collection=name, 
                        points_inserted=len(points))

    async def get_point(self, collection_name: str, point_id: str):
        with logfire.span("GetPoint") as span:
            span.set_attributes({
                "collection_name": collection_name,
                "point_id": point_id
            })
            point = await self.__manager.get_point_by_id(collection_name, point_id)
            span.set_attribute("point_found", bool(point))
            return point

    async def get_all_points(self, collection_name: str):
        with logfire.span("GetAllPoints") as span:
            span.set_attribute("collection_name", collection_name)
            points = await self.__manager.get_all_points(collection_name)
            span.set_attribute("points_returned", len(points))
            return points

    async def search(self, name: str, query: str, limit: int):
        with logfire.span("VectorSearch") as span:
            span.set_attributes({
                "collection_name": name,
                "query": query[:100],  # Truncate long queries
                "result_limit": limit
            })
            
            with logfire.span("QueryEmbedding"):
                query_vector = await self.__embeddings.embed_text(query)
            
            with logfire.span("QdrantSearch"):
                results = await self.__manager.search(name, query_vector, limit)
            
            span.set_attribute("results_count", len(results))
            return results

    async def update_point(self, collection_name: str, point_id: str, newdoc: dict):
        with logfire.span("UpdatePoint") as span:
            span.set_attributes({
                "collection_name": collection_name,
                "point_id": point_id,
                "content_length": len(newdoc.get('content', ''))
            })
            try:
                with logfire.span("EmbedUpdateContent"):
                    new_vector = await self.__embeddings.embed_text(newdoc['content'])
                
                with logfire.span("QdrantUpdate"):
                    await self.__manager.update_point(collection_name, point_id, new_vector, newdoc['payload'])
                
                logfire.info("Point updated successfully")
                return "Update successful"
            except Exception as e:
                logfire.record_exception(e)
                span.set_level("error")
                return "Failed to update point"

    async def delete_point(self, collection_name: str, point_id: str):
        with logfire.span("DeletePoint") as span:
            span.set_attributes({
                "collection_name": collection_name,
                "point_id": point_id
            })
            try:
                await self.__manager.point_delete(collection_name, [point_id])
                logfire.info("Point deleted successfully")
            except Exception as e:
                logfire.record_exception(e)
                span.set_level("error")
                raise