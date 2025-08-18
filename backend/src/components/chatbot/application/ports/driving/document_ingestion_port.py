from abc import ABC, abstractmethod
from typing import List, Optional

from src.components.chatbot.domain.value_objects import DocumentRetrievalVector, InputDocument
from src.components.chatbot.domain.value_objects import DocumentIngestionResult


class DocumentIngestionPort(ABC):
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
    ) -> DocumentIngestionResult:
        """
        Ingest a document into the system's knowledge base.
        
        This operation includes:
        1. Processing the document (extracting text and chunking)
        2. Generating embeddings for the chunks
        3. Storing the chunks in the vector database
        
        Args:
            document: The document to ingest
            chunk_size: Optional custom chunk size (characters)
            chunk_overlap: Optional custom overlap between chunks (characters)
            
        Returns:
            List[str]: IDs of the document chunks stored in the vector database
            
        Raises:
            ValueError: If the document type is not supported
            ProcessingError: If document processing fails
            StorageError: If storing in the vector database fails
        """
        pass
    
   