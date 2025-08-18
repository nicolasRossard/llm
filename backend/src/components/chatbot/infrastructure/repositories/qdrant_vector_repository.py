"""Qdrant Vector Repository implementing the VectorRepository interface."""
import logging
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
                 host: str = repo_settings.base_url,
                 port: int = repo_settings.grpc_port,
                 distance: models.Distance = models.Distance.COSINE
                 ):
        """Initialize the Qdrant Vector Repository.
        
        Attributes:
            embedding_port (EmbeddingPort): The embedding port instance for text vectorization.
            client (AsyncQdrantClient): Asynchronous client for Qdrant database operations.
            collection_parameters (dict): Configuration parameters for the Qdrant collection
                including name, distance metric, and vector dimensions.
        Note:
            The constructor automatically ensures the specified collection exists in the database
            by calling _ensure_collection_exists().
        """

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(
            f"Initializing QdrantVectorRepository with host={host}, port={port}, collection={collection_name}")

        self.embedding_port = embedding_port
        self.client = AsyncQdrantClient(
            host=host,
            grpc_port=port,
            prefer_grpc=True,
        )
        self.collection_parameters = {
            "name": collection_name,
            "distance": distance,
            "vector_size": self.embedding_port.fallback_dimension
        }

        self.logger.debug(f"Collection parameters: {self.collection_parameters}")

    async def _ensure_collection_exists(self) -> None:
        """Ensure the collection exists, create it if it doesn't."""

        try:
            collection_name = self.collection_parameters['name']
            self.logger.debug(f"Checking if collection '{collection_name}' exists")

            # Check if collection exists
            collection_exists = await self.client.collection_exists(collection_name)

            if not collection_exists:
                self.logger.info(f"Collection '{collection_name}' does not exist, creating it")
                # Collection doesn't exist, create it
                await self.client.create_collection(
                    collection_name=self.collection_parameters['name'],
                    vectors_config=models.VectorParams(
                        size=self.collection_parameters['vector_size'],
                        distance=self.collection_parameters['distance']
                    ),
                )
                self.logger.info(f"Successfully created collection '{collection_name}'")
            else:
                self.logger.debug(f"Collection '{collection_name}' already exists")
        except Exception as e:
            self.logger.error(f"Failed to ensure collection exists: {e}")
            raise

    async def search(self, query: Query, top_k: int = 5) -> List[DocumentRetrieval]:
        """Search for the most relevant documents given a query.
        
        Args:
            query: The domain query object
            top_k: Maximum number of results to return
            
        Returns:
            List of retrieved documents ranked by relevance
        """

        self.logger.info(f"Searching for documents with query: '{query.content[:100]}...' (top_k={top_k})")
        await self._ensure_collection_exists()

        try:
            # Generate embedding for the query
            query_vector = await self.embedding_port.generate_embedding(query.content)

            # Perform hybrid search using Qdrant
            search_result = await self.client.search(
                collection_name=self.collection_parameters['name'],
                query_vector=query_vector,
                limit=top_k,
                with_payload=True,
                with_vectors=False
            )

        except Exception as e:
            self.logger.error(f"Error during search operation: {e}")
            raise

        # Convert Qdrant results to domain objects
        results = [
            DocumentRetrieval(
                id=point.id,
                content=point.payload.get("content", ""),
                metadata=point.payload.get("metadata", {}),
                score=point.score
            )
            for point in search_result
        ]

        self.logger.info(f"Found {len(results)} documents for query")
        self.logger.debug(f"Search results scores: {[doc.score for doc in results]}")

        return results

    async def upsert(self, documents: List[DocumentRetrievalVector]) -> List[str]:
        """Insert or update documents in the vector storage.
        
        Args:
            documents: List of documents with their vectors
            
        Returns:
            List of IDs of documents successfully inserted
        """

        self.logger.info(f"Upserting {len(documents)} documents to collection '{self.collection_parameters['name']}'")

        try:
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

            self.logger.debug(f"Created {len(points)} points for upsert operation")

            await self.client.upsert(
                collection_name=self.collection_parameters['name'],
                points=points
            )

            document_ids = [str(doc.id) for doc in documents]
            self.logger.info(f"Successfully upserted {len(document_ids)} documents")
            self.logger.debug(f"Upserted document IDs: {document_ids[:5]}...")  # Log first 5 IDs

            return document_ids
        except Exception as e:
            self.logger.error(f"Error during upsert operation: {e}")
            raise
