from abc import ABC, abstractmethod
from typing import List

from src.components.rag.domain.value_objects import StoreDocumentResult, DocumentRetrievalVector


class VectorStorePort(ABC):
    """Abstract repository for vector-based document storage and retrieval.

    This interface defines the contract for searching and adding documents
    to a vector store, without binding to any specific technology (e.g., Qdrant, Pinecone).
    """

    @abstractmethod
    async def upsert(
            self,
            vector_documents: List[DocumentRetrievalVector],
    ) -> StoreDocumentResult:
        """
        Ingest a chunks from a document into the vector database.

        Args:
            vector_documents (List[DocumentRetrievalVector]): vectorized chunks to ingest into vector database

        Returns:
            List[str]: IDs of the document chunks stored in the vector database
        """
        pass

