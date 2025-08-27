"""Base class for Qdrant vector database interactions."""
import logging
from typing import Dict, Any

from src.components.rag.application.ports.driven import EmbeddingPort
from src.components.rag.infrastructure.persistence.repositories_settings import repo_settings
from qdrant_client import AsyncQdrantClient
from qdrant_client import models


class QdrantVectorBase:
    """Base class for Qdrant vector database operations.
    
    This class provides common functionality for interacting with a Qdrant vector database,
    including client initialization, collection management, and base operations.
    """

    def __init__(self,
                 fallback_dimension: int = repo_settings.fallback_dimension,
                 collection_name: str = repo_settings.collection_name,
                 host: str = repo_settings.base_url,
                 port: int = repo_settings.grpc_port,
                 distance: models.Distance = models.Distance.COSINE
                 ):
        """Initialize the Qdrant Vector Base.
        
        Args:
            fallback_dimension: Default vector dimension if model does not specify.
            collection_name: Name of the Qdrant collection to use.
            host: Hostname of the Qdrant server.
            port: gRPC port of the Qdrant server.
            distance: Distance metric to use for vector similarity.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(
            f"QdrantVectorBase :: Initializing with host={host}, port={port}, collection={collection_name}")

        self.client = AsyncQdrantClient(
            host=host,
            grpc_port=port,
            prefer_grpc=True,
        )
        self.collection_parameters = {
            "name": collection_name,
            "distance": distance,
            "vector_size": fallback_dimension
        }

        self.logger.debug(f"QdrantVectorBase :: Collection parameters: {self.collection_parameters}")

    async def _ensure_collection_exists(self) -> None:
        """Ensure the collection exists, create it if it doesn't.
        
        Raises:
            Exception: If there's an error creating or checking the collection.
        """
        try:
            collection_name = self.collection_parameters['name']
            self.logger.debug(f"QdrantVectorBase :: Checking if collection '{collection_name}' exists")

            # Check if collection exists
            collection_exists = await self.client.collection_exists(collection_name)

            if not collection_exists:
                self.logger.info(f"QdrantVectorBase :: Collection '{collection_name}' does not exist, creating it")
                # Collection doesn't exist, create it
                await self.client.create_collection(
                    collection_name=self.collection_parameters['name'],
                    vectors_config=models.VectorParams(
                        size=self.collection_parameters['vector_size'],
                        distance=self.collection_parameters['distance']
                    ),
                )
                self.logger.info(f"QdrantVectorBase :: Successfully created collection '{collection_name}'")
            else:
                self.logger.debug(f"QdrantVectorBase :: Collection '{collection_name}' already exists")
        except Exception as e:
            self.logger.error(f"QdrantVectorBase :: Failed to ensure collection exists: {e}")
            raise