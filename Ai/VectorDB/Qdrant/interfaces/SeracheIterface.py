from Qdrant.services.SearchService import SearchService
from fastapi import  Depends
import logfire
def get_service():
    return SearchService()

async def search(query: str, limit: int,service: SearchService = Depends(get_service)):
    logfire.info(f"Searching Iterface in Qdrant for query: {query}")
    try:
        result = await service.search( query, limit)
        return result
    except Exception as e:
        logfire.error(f"Error during search: {str(e)}")
        raise e


