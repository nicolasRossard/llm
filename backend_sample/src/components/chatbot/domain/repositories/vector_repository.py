from abc import ABC, abstractmethod
from typing import List

from src.components.chatbot.domain.value_objects import DocumentRetrievalVector, DocumentRetrieval
from src.components.chatbot.domain.value_objects.query import Query


class VectorRepository(ABC):
    """Abstract repository for vector-based document storage and retrieval.

    This interface defines the contract for searching and adding documents
    to a vector store, without binding to any specific technology (e.g., Qdrant, Pinecone).
    """

    @abstractmethod
    def search(self, query: Query, top_k: int = 5) -> List[DocumentRetrieval]:
        """Search for the most relevant documents given a query.

        Args:
            query (Query): The domain query object representing the search request.
            top_k (int, optional): Maximum number of results to return. Defaults to 5.

        Returns:
            List[DocumentRetrieval]: List of retrieved documents ranked by relevance.
        """
        pass

    @abstractmethod
    def upsert(self, documents: List[DocumentRetrievalVector]) -> List[str]:
        """Insert or update documents in the vector storage.

        Args:
            documents (List[DocumentRetrievalVector]): List of documents with their vectors to be
                inserted.

        Returns:
            List[str]: List of IDs of documents successfully inserted.
        """
        pass

