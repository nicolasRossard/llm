from datetime import datetime
import logging
from typing import List

from src.components.rag.application.ports.driven import VectorStorePort, EmbeddingPort
from src.components.rag.application.ports.driven.text_chunking_port import TextChunkingPort
from src.components.rag.application.ports.driven.text_extraction_port import TextExtractionPort
from src.components.rag.domain.value_objects import InputDocument, Embedding, DocumentRetrieval, DocumentRetrievalVector
from src.components.rag.domain.value_objects.extracted_content import ExtractedContent
from src.components.rag.domain.value_objects.input_document import StoreDocumentResult, StoreDocumentStatus


class IngestionServiceService:
    """
    Domain service for managing document operations.
    
    This service handles the business logic for document management operations,
    including document ingestion, retrieval, and deletion.
    """
    
    def __init__(
        self, 
        vector_store: VectorStorePort,
        embedding_port: EmbeddingPort,
        text_extraction_port: TextExtractionPort,
        text_chunking_port: TextChunkingPort
    ):
        """
        Initialize the document management service.
        
        Args:
            vector_store: Port for vector storage operations
            embedding_port: Port for generating vector embeddings from text
            text_extraction_port: Port for extracting text from documents
            text_chunking_port: Port for chunking text into smaller segments
        """
        self.vector_store = vector_store
        self.embedding_port = embedding_port
        self.text_extraction_port = text_extraction_port
        self.text_chunking_port = text_chunking_port
        self.logger = logging.getLogger(__name__)

    def add_metadata(self, extracted_content: ExtractedContent, input_document: InputDocument) -> ExtractedContent:
        """
        Add document-specific metadata to extracted content.

        Args:
            extracted_content (ExtractedContent): The extracted content with existing metadata.
            input_document (InputDocument): The input document containing filename and type.

        Returns:
            ExtractedContent: Updated extracted content with enhanced metadata.
        """
        self.logger.info("add_metadata :: Preparing metadata for chunking")
        metadata = extracted_content.metadata | {
            "filename": input_document.filename,
            "document_type": input_document.type,
            "ingested_at": datetime.now().isoformat(),
        }
        self.logger.debug(f"add_metadata :: Complete metadata: {metadata}")

        updated_extracted_content = ExtractedContent(
            text=extracted_content.text,
            metadata=metadata
        )

        return updated_extracted_content

    async def ingest_document(
        self, 
        input_document: InputDocument,
    ) -> StoreDocumentResult:
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
        self.logger.info(f"ingest_document :: Starting document ingestion for file: {input_document.filename}")
        
        # Extract text and metadata from document
        self.logger.info("ingest_document :: Extracting text and metadata from document")
        extracted_content: ExtractedContent = await self.text_extraction_port.extract_text(input_document)

        self.logger.info("ingest_document :: Adding specific metadata for the document")
        updated_extracted_content = self.add_metadata(extracted_content, input_document)

        # Chunk the text into smaller segments
        self.logger.info("ingest_document :: Chunking text into smaller segments")
        chunked_documents: List[DocumentRetrieval] = await self.text_chunking_port.chunk_text(updated_extracted_content)
        self.logger.debug(f"ingest_document :: Generated {len(chunked_documents)} chunks")
        
        # Create vector documents with embeddings
        self.logger.info("ingest_document :: Generating embeddings for document chunks")
        vectors = []
        for i, chunk in enumerate(chunked_documents):
            self.logger.debug(f"ingest_document :: Processing chunk {i+1}/{len(chunked_documents)}")
            
            # Generate embedding for each chunk
            embedding: Embedding = await self.embedding_port.embed_text(chunk.content)
            self.logger.debug(f"ingest_document :: Generated embedding with dimension: {len(embedding.vector) if embedding else 0}")
            
            # Create vector document
            vector = DocumentRetrievalVector(**chunk.model_dump(), vector=embedding.vector)
            vectors.append(vector)
        
        self.logger.debug(f"ingest_document :: Created {len(vectors)} vector documents")

        # Upsert the document vectors into the repository
        self.logger.info("ingest_document :: Storing document vectors in repository")
        stored_ids = await self.vector_store.upsert(vectors)
        self.logger.debug(f"ingest_document :: Successfully stored {len(stored_ids)} vectors with IDs: {stored_ids}")
        
        # Calculate statistics for the result
        self.logger.info("ingest_document :: Calculating ingestion statistics")
        total_chunks = len(vectors)
        ingested_chunks = len(stored_ids)
        failed_chunks = total_chunks - ingested_chunks
        
        # Determine status based on success rate
        if failed_chunks == 0:
            status = StoreDocumentStatus.SUCCESS
        elif ingested_chunks > 0:
            status = StoreDocumentStatus.PARTIAL
        else:
            status = StoreDocumentStatus.ERROR
        
        self.logger.debug(f"ingest_document :: Ingestion stats - Total: {total_chunks}, Ingested: {ingested_chunks}, Failed: {failed_chunks}, Status: {status}")
        self.logger.info(f"ingest_document :: Document ingestion completed with status: {status}")
        
        return StoreDocumentResult(
            total_chunks=total_chunks,
            ingested_chunks=ingested_chunks,
            failed_chunks=failed_chunks,
            status=status
        )