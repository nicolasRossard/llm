"""Qdrant Vector Repository implementing the VectorRepository interface."""

from typing import List
from uuid import uuid4

from src.components.chatbot.application.ports.driven import EmbeddingPort
from src.components.chatbot.domain.repositories import VectorRepository
from src.components.chatbot.domain.value_objects import DocumentRetrieval, DocumentRetrievalVector, Query
from src.components.chatbot.infrastructure.repositories.repositories_settings import repo_settings
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import PointStruct
from qdrant_client import models


class QdrantVectorRepository(VectorRepository):
    """Implementation of the VectorRepository using Qdrant.
    
    This repository is responsible for storing and retrieving document vectors
    using the Qdrant vector database.
    """
    
    def __init__(self,
                 embedding_port: EmbeddingPort,
                 collection_name: str = repo_settings.collection_name,
                 host: str = repo_settings.base_url, port: int = repo_settings.grpc_port,
                 distance: models.Distance = models.Distance.COSINE):
        """Initialize the Qdrant Vector Repository.
        
        Args:
            embedding_port: Port for generating embeddings from text content.
            collection_name: Name of the Qdrant collection to use for storage.
        """
        self.embedding_port = embedding_port
        self.client = AsyncQdrantClient(
            host=host,
            port=port,
            grpc=True
        )
        self.collection_parameters = {
            "name": collection_name,
            "distance": distance,
            "vector_size": self.embedding_port.fallback_dimension
        }

        self._ensure_collection_exists()
    
    async def _ensure_collection_exists(self) -> None:
        """Ensure the collection exists, create it if it doesn't."""
        
        # Check if collection exists
        collection_exists = await self.client.collection_exists(self.collection_name)
        
        if not collection_exists:
            # Collection doesn't exist, create it
            await self.client.create_collection(
            collection_name=self.collection_parameters['name'],
            vectors_config=models.VectorParams(
                size=self.collection_parameters['fallback_dimension'],
                distance=self.collection_parameters['distance']
            ),
            )
    
    async def search(self, query: Query, top_k: int = 5) -> List[DocumentRetrieval]:
        """Search for the most relevant documents given a query.
        
        Args:
            query: The domain query object
            top_k: Maximum number of results to return
            
        Returns:
            List of retrieved documents ranked by relevance
        """

        # Generate embedding for the query
        # query_vector = await self.embedding_port.generate_embedding(query.content)
        
        # This would be a real implementation calling the Qdrant search API
        # For mock purposes, return dummy documents
        return [
            DocumentRetrieval(
                id=uuid4(),
                content=f"This is document {i} content that is relevant to the query: {query.content}",
                metadata={"source": f"source{i}", "title": f"Document {i}"},
                score=0.9 - (i * 0.1)
            )
            for i in range(min(3, top_k))
        ]
    
    async def upsert(self, documents: List[DocumentRetrievalVector]) -> List[str]:
        """Insert or update documents in the vector storage.
        
        Args:
            documents: List of documents with their vectors
            
        Returns:
            List of IDs of documents successfully inserted
        """
        await self._ensure_collection_exists()  # Check if collection exists before upserting
        
        points = [
            PointStruct(
                id=str(doc.id),
                vector=doc.vector,
                payload={
                    "content": doc.content,
                    "metadata": doc.metadata or {}
                }
            )
            for doc in documents
        ]
        
        await self.client.upsert(
            collection_name=self.collection_parameters['name'],
            points=points
        )
        
        return [str(doc.id) for doc in documents]
