from Qdrant.services.QdrantService import QdrantService
from typing import List, Optional
from fastapi import Depends
import logfire

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




