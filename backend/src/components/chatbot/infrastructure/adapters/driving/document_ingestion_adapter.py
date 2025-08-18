from src.components.chatbot.application.ports.driving.document_ingestion_port import DocumentIngestionPort
from src.components.chatbot.application.services import DocumentProcessingService
from src.components.chatbot.domain.value_objects import InputDocument
from src.components.chatbot.domain.value_objects.input_document import DocumentIngestionResult


class DocumentIngestionAdapter(DocumentIngestionPort):
    """Primary adapter implementing the Document ingestion interface.

    This adapter follows the Hexagonal Architecture pattern, serving as the
    boundary between external systems and the application core. It translates
    external requests into calls to the application service.

    This is a clear example of a Driving Adapter (Primary Adapter) that conforms
    to a Driving Port (Primary Port).
    """

    def __init__(self, document_processing_service: DocumentProcessingService):
        """Initialize the adapter with required dependencies.

        Args:
            document_processing_service: The application service that contains the core business logic.
        """
        self.document_processing_service = document_processing_service

    async def ingest_document(self, document: InputDocument) -> DocumentIngestionResult:
        """Ingest a document into the system.

        This method processes the document and returns the result of the ingestion.

        Args:
            document: A dictionary representing the document to be ingested.

        Returns:
            A dictionary containing the result of the ingestion process.
        """
        return await self.document_processing_service.ingest_document(document)
