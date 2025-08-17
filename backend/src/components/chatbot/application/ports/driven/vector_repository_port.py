from abc import ABC, abstractmethod
from typing import List, Any

from src.components.chatbot.domain.value_objects import DocumentRetrievalVector


class VectorRepositoryPort(ABC):
    """Port interface for interacting with a vector store engine."""

    @abstractmethod
    async def upsert(self, document: DocumentRetrievalVector) -> None:
        """Insert or update a vector document in the store.

        Args:
            document: The vector document to insert or update.

        Returns:
            None
        """
        pass

    @abstractmethod
    async def search(self, vector: List[float], top_k: int = 5) -> List[DocumentRetrievalVector]:
        """Search for the most similar documents to the given vector.

        Args:
            vector: Query vector used for similarity search.
            top_k: Maximum number of results to retrieve.

        Returns:
            List[DocumentSource]: List of search results ordered by similarity.
        """
        pass

    # @abstractmethod
    # async def delete(self, ids: List[str]) -> None:
    #     """Delete documents from the store by their IDs.
    #
    #     Args:
    #         ids: List of document IDs to delete.
    #
    #     Returns:
    #         None
    #     """
    #     pass
    #
    # @abstractmethod
    # async def create_collection(
    #     self,
    #     name: str,
    #     vector_size: int,
    #     distance: str = "cosine",
    #     **kwargs: Any
    # ) -> None:
    #     """Create a collection in the vector store.
    #
    #     Args:
    #         name: Name of the collection to create.
    #         vector_size: Dimensionality of the vectors.
    #         distance: Distance metric to use ('cosine', 'euclidean', etc.).
    #         **kwargs: Additional vendor-specific parameters.
    #
    #     Returns:
    #         None
    #     """
    #     pass
