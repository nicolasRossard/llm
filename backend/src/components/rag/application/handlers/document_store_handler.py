from src.components.rag.application.ports.driving.document_store_port import DocumentStorePort
from src.components.rag.domain.services.document_store_service import DocumentStoreService
from src.components.rag.domain.value_objects import InputDocument
from src.components.rag.domain.value_objects.input_document import StoreDocumentResult


class DocumentStoreHandler(DocumentStorePort):
    def __init__(self, document_store_service: DocumentStoreService):
        self.document_store_service = document_store_service

    async def add_document(self, document: InputDocument) -> StoreDocumentResult:
        return await self.document_store_service.ingest_document(document)
