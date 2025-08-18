from datetime import datetime
from typing import List

from src.components.chatbot.application.ports.driven.text_extraction_port import TextExtractionPort
from src.components.chatbot.application.ports.driven.text_chunking_port import TextChunkingPort
from src.components.chatbot.application.ports.driven import EmbeddingPort
from src.components.chatbot.domain.repositories import VectorRepository
from src.components.chatbot.domain.value_objects import InputDocument, DocumentRetrievalVector
from src.components.chatbot.domain.value_objects.input_document import DocumentIngestionResult, IngestionStatus


class ManageDocuments:
    """
    Domain service for managing document operations.
    
    This service handles the business logic for document management operations,
    including document ingestion, retrieval, and deletion.
    """
    
    def __init__(
        self, 
        vector_repository: VectorRepository,
        embedding_port: EmbeddingPort,
        text_extraction_port: TextExtractionPort,
        text_chunking_port: TextChunkingPort
    ):
        """
        Initialize the document management service.
        
        Args:
            vector_repository: Repository for storing and retrieving document vectors
            embedding_port: Port for generating vector embeddings from text
            text_extraction_port: Port for extracting text from documents
            text_chunking_port: Port for chunking text into smaller segments
        """
        self.vector_repository = vector_repository
        self.embedding_port = embedding_port
        self.text_extraction_port = text_extraction_port
        self.text_chunking_port = text_chunking_port

    async def ingest_document(
        self, 
        input_document: InputDocument,
    ) -> DocumentIngestionResult:
        """
        Add a new document to the repository by processing, embedding, and storing it.

        This method takes an input document, processes it into chunks, generates embeddings
        for each chunk, and stores the resulting vectors in the vector repository for
        retrieval purposes.

        Args:
            input_document: The input document to be processed and added

        Returns:
            DocumentIngestionResult: Result object containing status and information about stored vectors

        Raises:
            ValueError: If document type is not supported
            ProcessingError: If document processing fails
        """
        # Extract text and metadata from document
        text, base_metadata = await self.text_extraction_port.extract_text(input_document)
        
        # Prepare metadata for chunking
        metadata = base_metadata | {
            "filename": input_document.filename,
            "document_type": input_document.type.value,
            "ingested_at": datetime.now().isoformat(),
        }
        
        # Chunk the text into smaller segments
        chunked_documents = await self.text_chunking_port.chunk_text(text, metadata)
        
        # Create vector documents with embeddings
        vectors = []
        for chunk in chunked_documents:
            # Generate embedding for each chunk
            embedding = await self.embedding_port.generate_embedding(chunk.content)
            
            # Create vector document
            vector = DocumentRetrievalVector(
                content=chunk.content,
                vector=embedding,
                metadata=chunk.metadata
            )
            vectors.append(vector)

        # Upsert the document vectors into the repository
        stored_ids = await self.vector_repository.upsert(vectors)
        
        # Calculate statistics for the result
        total_chunks = len(vectors)
        ingested_chunks = len(stored_ids)
        failed_chunks = total_chunks - ingested_chunks
        
        # Determine status based on success rate
        if failed_chunks == 0:
            status = IngestionStatus.SUCCESS
        elif ingested_chunks > 0:
            status = IngestionStatus.PARTIAL
        else:
            status = IngestionStatus.ERROR
        
        return DocumentIngestionResult(
            total_chunks=total_chunks,
            ingested_chunks=ingested_chunks,
            failed_chunks=failed_chunks,
            status=status
        )
    