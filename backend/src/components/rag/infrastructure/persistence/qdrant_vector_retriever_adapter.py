"""Qdrant implementation of the VectorRetrieverPort."""
import logging
from typing import List

from src.components.rag.application.ports.driven import VectorRetrieverPort, EmbeddingPort
from src.components.rag.domain.value_objects import DocumentRetrieval
from src.components.rag.infrastructure.persistence.qdrant_vector_base import QdrantVectorBase


class QdrantVectorRetrieverAdapter(VectorRetrieverPort, QdrantVectorBase):
    """Implementation of VectorRetrieverPort using Qdrant.
    
    This adapter handles retrieving vectorized documents from the Qdrant vector database.
    """

    def __init__(self, **kwargs):
        """Initialize the Qdrant Vector Retriever Adapter.
        
        Args:
            **kwargs: Additional arguments to pass to the QdrantVectorBase constructor.
        """
        super().__init__(**kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("QdrantVectorRetrieverAdapter :: Initialized")

    async def search(self, query: list[float], top_k: int = 5, *args, **kwargs) -> List[DocumentRetrieval]:
        """Search for the most relevant documents given a query vector.
        
        Args:
            query: Vector representation of the query
            top_k: Maximum number of results to return
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            List of retrieved documents ranked by relevance
            
        Raises:
            Exception: If there's an error during the search operation
        """
        self.logger.info(f"QdrantVectorRetrieverAdapter :: Searching for documents (top_k={top_k})")
        await self._ensure_collection_exists()

        try:
            # Perform search using Qdrant
            search_result = await self.client.search(
                collection_name=self.collection_parameters['name'],
                query_vector=query,
                limit=top_k,
                with_payload=True,
                with_vectors=False
            )

        except Exception as e:
            self.logger.error(f"search :: Error during search operation: {e}")
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

        self.logger.info(f"QdrantVectorRetrieverAdapter :: Found {len(results)} documents")
        self.logger.debug(f"QdrantVectorRetrieverAdapter :: Search results scores: {[doc.score for doc in results]}")

        return results


if __name__ == "__main__":
    """
    Main entry point for testing QdrantVectorRetrieverAdapter.
    """
    import asyncio

    async def main():
        adapter = QdrantVectorRetrieverAdapter()
        import random
        query_vector = [random.uniform(-1, 1) for _ in range(
            768)]  # Random query vector of 768 elements        adapter.logger.info("__main__ :: Starting test search")
        try:
            results = await adapter.search(query=query_vector, top_k=3)
            adapter.logger.debug(f"__main__ :: Search results: {results}")
        except Exception as e:
            adapter.logger.error(f"__main__ :: Exception during test: {e}")

    asyncio.run(main())