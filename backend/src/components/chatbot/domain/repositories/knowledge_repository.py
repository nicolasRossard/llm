from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class KnowledgeRepository(ABC):
    """
    Repository interface for the knowledge base.
    Defines search operations within the knowledge base.
    """

    @abstractmethod
    async def find_relevant_documents(
            self,
            query: str,
            limit: int = 5,
            filters: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Finds relevant documents for a query"""
        pass

    @abstractmethod
    async def add_document(self, document: str, metadata: Dict[str, Any]) -> str:
        """Adds a document to the knowledge base"""
        pass

    @abstractmethod
    async def update_document(self, document_id: str, document: str, metadata: Dict[str, Any]) -> bool:
        """Updates an existing document"""
        pass

    @abstractmethod
    async def delete_document(self, document_id: str) -> bool:
        """Deletes a document from the knowledge base"""
        pass

    @abstractmethod
    async def search_by_metadata(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Searches for documents by metadata"""
        pass

    @abstractmethod
    async def get_document_count(self) -> int:
        """Returns the total number of documents"""
        pass
