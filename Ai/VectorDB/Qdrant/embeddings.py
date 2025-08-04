from typing import List
from qdrant_client.http.models import PointStruct
from sentence_transformers import SentenceTransformer
import logfire
import asyncio


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
