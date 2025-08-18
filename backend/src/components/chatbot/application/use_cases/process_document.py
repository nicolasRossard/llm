from datetime import datetime
from typing import List, Dict, Any

from src.components.chatbot.application.ports.driven.text_extraction_port import TextExtractionPort
from src.components.chatbot.application.ports.driven.text_chunking_port import TextChunkingPort
from src.components.chatbot.application.ports.driven import EmbeddingPort
from src.components.chatbot.domain.repositories import VectorRepository
from src.components.chatbot.domain.value_objects.input_document import InputDocument
from src.components.chatbot.domain.value_objects import DocumentRetrievalVector


class ProcessDocument:
    """Application use case for processing and ingesting documents into the vector database.
    
    This use case handles the full document processing pipeline:
    1. Extract text from the document using TextExtractionPort
    2. Chunk the text into manageable segments using TextChunkingPort
    3. Generate embeddings for each chunk
    4. Store the chunks and their embeddings in the vector database
    
    Follows hexagonal architecture by depending on ports (interfaces)
    rather than concrete implementations.
    """
    
    def __init__(
        self,
        text_extraction_port: TextExtractionPort,
        text_chunking_port: TextChunkingPort,
        embedding_port: EmbeddingPort,
        vector_repository: VectorRepository
    ):
        """Initialize the use case with its dependencies.
        
        Args:
            text_extraction_port: Port for document text extraction
            text_chunking_port: Port for chunking text into segments
            embedding_port: Port for generating embeddings from text
            vector_repository: Repository for storing vectors in the database
        """
        self.text_extraction_port = text_extraction_port
        self.text_chunking_port = text_chunking_port
        self.embedding_port = embedding_port
        self.vector_repository = vector_repository
    
    async def execute(self, document: InputDocument) -> List[str]:
        """Execute the document processing pipeline.
        
        Args:
            document: The input document to process
            
        Returns:
            List[str]: IDs of the chunks stored in the vector database
            
        Raises:
            ValueError: If document type is not supported
        """
        # Extract text from document
        text, metadata = await self.text_extraction_port.extract_text(document)
        
        # Prepare metadata for chunking
        metadata = metadata | {
            "filename": document.filename,
            "ingested_at": datetime.now().isoformat(),
        }
        
        # Chunk the text into smaller segments
        document_retrievals = await self.text_chunking_port.chunk_text(text, metadata)
        
        # Create document retrieval vector objects with embeddings
        doc_chunks = []
        for i, chunk in enumerate(document_retrievals):
            # Add chunk index to metadata
            chunk_metadata = chunk.metadata | {"chunk_index": i}
            
            # Generate embedding for the chunk
            vector = await self.embedding_port.generate_embedding(chunk.content)
            
            # Create document retrieval vector object
            doc_chunk = DocumentRetrievalVector(
                content=chunk.content,
                vector=vector,
                metadata=chunk_metadata
            )
            doc_chunks.append(doc_chunk)
        
        # Store chunks in vector database
        chunk_ids = await self.vector_repository.upsert(doc_chunks)
        
        return chunk_ids