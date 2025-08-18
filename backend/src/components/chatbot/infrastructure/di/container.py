"""Dependency injection container for the chatbot component."""

from src.components.chatbot.application.ports.driven import (
    LLMPort, 
    EmbeddingPort,
    TextExtractionPort,
    TextChunkingPort
)
from src.components.chatbot.application.ports.driving import (
    ChatbotPort,
    DocumentIngestionPort
)
from src.components.chatbot.application.services.chatbot_service import ChatbotService
from src.components.chatbot.application.services.document_processing_service import DocumentProcessingService
from src.components.chatbot.domain.repositories import VectorRepository
from src.components.chatbot.infrastructure.adapters.driven import (
    OllamaLLMAdapter,
    OllamaEmbeddingAdapter,
    PyPDFTextExtractionAdapter,
    NaiveTextChunkingAdapter
)
from src.components.chatbot.infrastructure.adapters.driving import (
    ChatbotAdapter,
    DocumentIngestionAdapter
)
from src.components.chatbot.infrastructure.repositories import QdrantVectorRepository
from src.components.chatbot.infrastructure.config import chatbot_settings, document_ingestion_settings


# ---------------------- Domain repositories ----------------------
def get_vector_repository() -> VectorRepository:
    """Get the implementation of the vector repository."""
    # Get the embedding port for generating vector embeddings

    embedding_port = get_embedding_port()

    # Use Qdrant for vector storage
    return QdrantVectorRepository(
        collection_name=chatbot_settings.ollama.vector_collection,
        embedding_port=embedding_port
    )

# ---------------------- Application ports ----------------------
# Driven ports (secondary) implementations
def get_llm_port() -> LLMPort:
    """Get the implementation of the LLM port."""
    if chatbot_settings.provider.lower() == "ollama":
        # Using Ollama for LLM generation
        return OllamaLLMAdapter(
            base_url=chatbot_settings.ollama.base_url,
            model=chatbot_settings.ollama.llm_model
        )


def get_embedding_port() -> EmbeddingPort:
    """Get the implementation of the embedding port."""
    if chatbot_settings.provider.lower() == "ollama":
        # Using Ollama for embeddings
        return OllamaEmbeddingAdapter(
            base_url=chatbot_settings.ollama.base_url,
            model=chatbot_settings.ollama.embedding_model,
            fallback_dimension=chatbot_settings.ollama.vector_dimension
        )

def get_text_extraction_port() -> TextExtractionPort:
    """Get the implementation of the text extraction port."""
    return PyPDFTextExtractionAdapter()


def get_text_chunking_port() -> TextChunkingPort:
    """Get the implementation of the text chunking port."""
    return NaiveTextChunkingAdapter(
        chunk_size=document_ingestion_settings.chunk_size,
        overlap=document_ingestion_settings.overlap
    )


# ---------------------- Application service ----------------------
def get_document_processing_service() -> DocumentProcessingService:
    """Get the document ingestion application service with all its dependencies."""
    # Get all required dependencies
    text_extraction_port = get_text_extraction_port()
    text_chunking_port = get_text_chunking_port()
    vector_repository = get_vector_repository()
    embedding_port = get_embedding_port()
    # Create the application service with the dependencies
    return DocumentProcessingService(
        text_extraction_port=text_extraction_port,
        text_chunking_port=text_chunking_port,
        vector_repository=vector_repository,
        embedding_port=embedding_port
    )


def get_chatbot_service() -> ChatbotService:
    """Get the chatbot application service with all its dependencies."""
    # Get all required dependencies
    llm_port = get_llm_port()
    vector_repository = get_vector_repository()

    # Create the application service with the dependencies
    return ChatbotService(
        llm_port=llm_port,
        vector_repository=vector_repository,
        top_k=chatbot_settings.ollama.top_k_documents,
        use_rag=chatbot_settings.ollama.use_rag
    )