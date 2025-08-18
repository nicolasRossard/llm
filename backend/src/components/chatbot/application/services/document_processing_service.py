import time
from backend.src.components.chatbot.domain.services.manage_documents import ManageDocuments
from backend.src.components.chatbot.domain.value_objects.input_document import DocumentIngestionResult, InputDocument
from src.components.chatbot.application.ports.driven.text_extraction_port import TextExtractionPort
from src.components.chatbot.application.ports.driven.text_chunking_port import TextChunkingPort
from src.components.chatbot.application.ports.driven import EmbeddingPort
from src.components.chatbot.domain.repositories import VectorRepository


class DocumentProcessingService:
    """
    Process to manage document
    The service delegates core processing to the ManageDocuments domain service
    while tracking detailed performance metrics throughout the pipeline.
    """
    
    def __init__(
        self,
        vector_repository: VectorRepository,
        embedding_port: EmbeddingPort,
        text_extraction_port: TextExtractionPort,
        text_chunking_port: TextChunkingPort
    ):
        """Initialize the use case with required ports and repositories.
        
        Args:
            vector_repository: Repository for storing and retrieving document vectors
            embedding_port: Port for generating vector embeddings from text
            text_extraction_port: Port for extracting text from documents
            text_chunking_port: Port for chunking text into smaller segments
        """
        # Create the manage_documents service with the provided dependencies
        self.vector_repository = vector_repository
        self.manage_documents = ManageDocuments(
            vector_repository=vector_repository,
            embedding_port=embedding_port,
            text_extraction_port=text_extraction_port,
            text_chunking_port=text_chunking_port
        )
    
    async def ingest_document(
        self, 
        document: InputDocument,
    ) -> DocumentIngestionResult:
        """Execute the complete document processing and storage workflow.
        
        Processing steps:
        1. Content extraction - Extract text from the input document
        2. Text chunking - Split document into manageable chunks with overlap
        3. Preprocessing - Clean and normalize text content
        4. Embedding generation - Create vector embeddings for each chunk
        5. Vector storage - Store embeddings in the vector database
        6. Metrics collection - Gather performance and success statistics
        
        Args:
            document: The input document to process and ingest
            
        Returns:
            DocumentIngestionResult: Result containing:
                - Ingestion statistics (total/successful/failed chunks)
                - Processing status
                - Performance metrics
                - Error details if any failures occurred
        """
        # Start timing the overall process
        start_time = time.time()
        
        # Process the document using the domain service
        result = await self.manage_documents.ingest_document(
            input_document=document,
        )
        
        # Calculate total processing time
        total_time = time.time() - start_time
        
        # Compile all metrics
        metrics = {
            # Basic document info
            "document_size_bytes": len(document.content),
            "document_type": document.type.value,
            "filename": document.filename,
                        
            # Timing
            "total_processing_time_ms": int(total_time * 1000),
            
            # Result statistics
            "total_chunks": result.total_chunks,
            "ingested_chunks": result.ingested_chunks,
            "failed_chunks": result.failed_chunks,
            "ingestion_status": result.status.value,
        }
        
        # Add rate metrics
        if total_time > 0:
            metrics["chunks_per_second"] = round(result.total_chunks / total_time, 2)
        else:
            metrics["chunks_per_second"] = 0
            
        # Add success rate
        if result.total_chunks > 0:
            metrics["ingestion_success_rate"] = round((result.ingested_chunks / result.total_chunks) * 100, 2)
        else:
            metrics["ingestion_success_rate"] = 0
            
        # Add document ID if available
        if hasattr(document, 'id') and document.id:
            metrics["document_id"] = document.id
            
        # Merge any metrics from the result if available
        if hasattr(result, 'metrics') and result.metrics:
            metrics.update(result.metrics)
        result.metrics = metrics  
        return result