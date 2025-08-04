from Qdrant.services.SearchService import SearchService
from fastapi import APIRouter, Depends, Query
import asyncio

def get_service():
    return SearchService()

router = APIRouter()

@router.post("/search")
async def search(
    search_query: str = Query(..., description="The search query string"),
    limit: int = Query(10, description="The maximum number of results to return"),
    service: SearchService = Depends()
):
    search_response = await service.search(search_query, limit)
    return search_response

