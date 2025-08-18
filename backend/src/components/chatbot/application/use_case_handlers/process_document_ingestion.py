from src.components.chatbot.application.ports.driving import DocumentIngestionPort
from src.components.chatbot.application.services import DocumentProcessingService
from src.components.chatbot.domain.value_objects.input_document import InputDocument, DocumentIngestionResult


class ProcessDocumentIngestion(DocumentIngestionPort):
    """
    Use case for processing documents and storing them in the vector database.
    
    This class coordinates the document ingestion workflow by delegating to
    the ManageDocuments domain service while tracking performance metrics.
    """
    
    def __init__(
        self,
        document_processing_service: DocumentProcessingService
    ):
        """Initialize the use case with the domain service.
        
        Args:
            document_processing_service: service for document management
        """
        self.document_processing_service = document_processing_service
    
    async def ingest_document(
        self, 
        document: InputDocument,
    ) -> DocumentIngestionResult:
        return await self.document_processing_service.ingest_document(
            input_document=document
        )