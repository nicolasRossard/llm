from abc import ABC, abstractmethod
from typing import List

from src.components.rag.domain.value_objects import InputDocument, InputDocumentResult


class IngestionPort(ABC):
    """
    Driving port (entry point) for document ingestion functionality.

    This port defines the interface through which external systems (such as API controllers
    or user interfaces) can interact with the document processing and ingestion capabilities
    of the application.
    """

    @abstractmethod
    async def ingest_document(
            self,
            document: InputDocument,
    ) -> InputDocumentResult:
        """
        Ingest a document into the system's knowledge base.

        This operation includes:
        TODO add step save into DB
        1. Processing the document (extracting text and chunking)
        2. Generating embeddings for the chunks
        3. Storing the chunks in the vector database

        Args:
            document (InputDocument): The document to ingest

        Returns:
            InputDocumentResult: Ingestion details
        """
        pass

