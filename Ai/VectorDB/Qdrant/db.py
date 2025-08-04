from qdrant_client import QdrantClient,AsyncQdrantClient
from fastapi import Request

async def get_client(request: Request) -> AsyncQdrantClient:
    """Dependency to get the shared Qdrant client"""
    return request.app.state.qdrant_client
