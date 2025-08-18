from datetime import datetime
from typing import List
import logging

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
        self.logger = logging.getLogger(__name__)

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
        self.logger.info(f"Starting document ingestion for file: {input_document.filename}")
        
        # Extract text and metadata from document
        self.logger.info("Extracting text and metadata from document")
        text, base_metadata = await self.text_extraction_port.extract_text(input_document)
        self.logger.debug(f"Extracted text length: {len(text)} characters, metadata: {base_metadata}")

        # Prepare metadata for chunking
        self.logger.info("Preparing metadata for chunking")
        metadata = base_metadata | {
            "filename": input_document.filename,
            "document_type": input_document.type.value,
            "ingested_at": datetime.now().isoformat(),
        }
        self.logger.debug(f"Complete metadata: {metadata}")
        
        # Chunk the text into smaller segments
        self.logger.info("Chunking text into smaller segments")
        chunked_documents = await self.text_chunking_port.chunk_text(text, metadata)
        self.logger.debug(f"Generated {len(chunked_documents)} chunks")
        
        # Create vector documents with embeddings
        self.logger.info("Generating embeddings for document chunks")
        vectors = []
        for i, chunk in enumerate(chunked_documents):
            self.logger.debug(f"Processing chunk {i+1}/{len(chunked_documents)}")
            
            # Generate embedding for each chunk
            embedding = await self.embedding_port.generate_embedding(chunk.content)
            self.logger.debug(f"Generated embedding with dimension: {len(embedding) if embedding else 0}")
            
            # Create vector document
            vector = DocumentRetrievalVector(**chunk.model_dump(), vector=embedding)
            vectors.append(vector)
        
        self.logger.debug(f"Created {len(vectors)} vector documents")

        # Upsert the document vectors into the repository
        self.logger.info("Storing document vectors in repository")
        stored_ids = await self.vector_repository.upsert(vectors)
        self.logger.debug(f"Successfully stored {len(stored_ids)} vectors with IDs: {stored_ids}")
        
        # Calculate statistics for the result
        self.logger.info("Calculating ingestion statistics")
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
        
        self.logger.debug(f"Ingestion stats - Total: {total_chunks}, Ingested: {ingested_chunks}, Failed: {failed_chunks}, Status: {status}")
        self.logger.info(f"Document ingestion completed with status: {status}")
        
        return DocumentIngestionResult(
            total_chunks=total_chunks,
            ingested_chunks=ingested_chunks,
            failed_chunks=failed_chunks,
            status=status
        )