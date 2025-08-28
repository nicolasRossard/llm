"""Qdrant implementation of the VectorStorePort."""
import logging
import time
from typing import List

from src.components.rag.application.ports.driven import VectorStorePort, EmbeddingPort
from src.components.rag.domain.value_objects import DocumentRetrievalVector, StoreDocumentResult
from src.components.rag.domain.value_objects.input_document import StoreDocumentStatus
from src.components.rag.infrastructure.persistence.qdrant_vector_base import QdrantVectorBase
from qdrant_client.models import PointStruct


class QdrantVectorStoreAdapter(VectorStorePort, QdrantVectorBase):
    """Implementation of VectorStorePort using Qdrant.
    
    This adapter handles storing vectorized documents in the Qdrant vector database.
    """

    def __init__(self, **kwargs):
        """Initialize the Qdrant Vector Store Adapter.
        
        Args:
            embedding_port: The embedding port instance for text vectorization.
            **kwargs: Additional arguments to pass to the QdrantVectorBase constructor.
        """
        super().__init__(**kwargs)
        self.logger.info("QdrantVectorStoreAdapter :: Initialized")

    async def upsert(self, vector_documents: List[DocumentRetrievalVector]) -> StoreDocumentResult:
        """Insert or update documents in the vector storage.
        
        Args:
            vector_documents: List of documents with their vectors
            
        Returns:
            InputDocumentResult: Result object containing IDs of successfully inserted documents
            
        Raises:
            Exception: If there's an error during the upsert operation
        """
        self.logger.info(f"upsert :: Upserting {len(vector_documents)} documents")

        try:
            await self._ensure_collection_exists()  # Check if collection exists before upserting
            start_time = time.time()
            points = [
                PointStruct(
                    id=str(doc.id),
                    vector=doc.vector,
                    payload={
                        "content": doc.content,
                        "metadata": doc.metadata or {}
                    }
                )
                for doc in vector_documents
            ]
            self.logger.debug(f"QdrantVectorStoreAdapter :: Created {len(points)} points for upsert")
            await self.client.upsert(
                collection_name=self.collection_parameters['name'],
                points=points
            )

            self.logger.info(f"QdrantVectorStoreAdapter :: Successfully upserted {len(points)} documents")

            # Return InputDocumentResult with successful IDs
            return StoreDocumentResult(
                total_chunks=len(points),
                ingested_chunks=len(points),
                status=StoreDocumentStatus.SUCCESS,
                failed_chunks=0,  # Qdrant do not provide partially failed
                metrics={"processing_time_ms": (time.time() - start_time) * 1000}
              )
        except Exception as e:
            self.logger.error(f"QdrantVectorStoreAdapter :: Error during upsert operation: {e}")
            raise Exception(f"Error during upsert operation: {e}")


