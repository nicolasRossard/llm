from typing import List
from enum import Enum

from pydantic import BaseModel, Field

from src.components.chatbot.application.ports.driven import EmbeddingPort, DocumentProcessingPort
from src.components.chatbot.domain.repositories import VectorRepository
from src.components.chatbot.domain.value_objects import InputDocument, DocumentRetrievalVector


class IngestionStatus(Enum):
    SUCCESS = "success"  # All vectors were inserted
    PARTIAL = "partial"  # Some vectors were inserted, but not all
    ERROR = "error"      # No vectors were inserted


class DocumentIngestionResult(BaseModel):
    status: IngestionStatus
    vectors: List
    stored_ids: List[str] = Field(default_factory=list)
    failed_ids: List[str] = Field(default_factory=list)


class ManageDocuments:
    def __init__(self, vector_repository: VectorRepository, embedding_port: EmbeddingPort,
                 document_processing_port: DocumentProcessingPort):
        self.vector_repository = vector_repository
        self.embedding_port = embedding_port
        self.document_processing_port = document_processing_port

    def ingest_document(self, input_document: InputDocument) -> DocumentIngestionResult:
        """Add a new document to the repository by processing, embedding, and storing it.

        This method takes an input document, processes it into chunks, generates embeddings
        for each chunk, and stores the resulting vectors in the vector repository for
        retrieval purposes.

        Args:
            input_document (InputDocument): The input document to be processed and added to the repository.

        Returns:
            DocumentIngestionResult: Result object containing status and information about stored vectors.

        Raises:
            TODO

        Example:
            >>> TODO
        """
        chunked_documents = self.document_processing_port.process_document(input_document)
        vectors = []

        for chunk in chunked_documents:
            # Generate embedding for each chunk
            embedding = self.embedding_port.generate_embedding(chunk.content)
            # Prepare the document for vector storage
            vector_data = {
                "id": chunk.id,
                "content": chunk.content,
                "embedding": embedding,
                "metadata": chunk.metadata
            }
            vectors.append(DocumentRetrievalVector(**vector_data))

        # Upsert the document into the vector repository
        stored_ids = self.vector_repository.upsert(vectors)
        
        # Calculate failed IDs
        all_ids = [vector.id for vector in vectors]
        failed_ids = [id for id in all_ids if id not in stored_ids]
        
        # Determine status based on success rate
        if len(stored_ids) == len(vectors):
            status = IngestionStatus.SUCCESS
        elif len(stored_ids) > 0:
            status = IngestionStatus.PARTIAL
        else:
            status = IngestionStatus.ERROR
        
        return DocumentIngestionResult(
            status=status,
            vectors=vectors,
            stored_ids=stored_ids,
            failed_ids=failed_ids
        )
