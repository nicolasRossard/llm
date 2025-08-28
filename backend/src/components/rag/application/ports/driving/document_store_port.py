from abc import ABC, abstractmethod
from typing import List

from src.components.rag.domain.value_objects import InputDocument, StoreDocumentResult


class DocumentStorePort(ABC):
    """
    Driving port (entry point) for document ingestion functionality.

    This port defines the interface through which external systems (such as API controllers
    or user interfaces) can interact with the document processing and ingestion capabilities
    of the application.
    """

    @abstractmethod
    async def add_document(
            self,
            document: InputDocument,
    ) -> StoreDocumentResult:
        """
        Ingest a document into the system's knowledge base.
        """
        pass

