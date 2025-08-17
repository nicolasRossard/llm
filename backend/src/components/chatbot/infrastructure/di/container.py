"""Dependency injection container for the chatbot component."""

from src.components.chatbot.application.ports.driven import LLMPort, EmbeddingPort
from src.components.chatbot.application.ports.driving import ChatbotPort
from src.components.chatbot.application.services.chatbot_service import ChatbotService
from src.components.chatbot.domain.repositories import VectorRepository
from src.components.chatbot.infrastructure.adapters.driven import (
    OllamaLLMAdapter,
    OllamaEmbeddingAdapter
)
from src.components.chatbot.infrastructure.adapters.driving import ChatbotAdapter
from src.components.chatbot.infrastructure.repositories import QdrantVectorRepository
from src.components.chatbot.infrastructure.config import settings


# Driven ports (secondary) implementations
def get_llm_port() -> LLMPort:
    """Get the implementation of the LLM port."""
    if settings.provider.lower() == "ollama":
        # Using Ollama for LLM generation
        return OllamaLLMAdapter(
            base_url=settings.ollama.base_url,
            model=settings.ollama.llm_model
        )


def get_embedding_port() -> EmbeddingPort:
    """Get the implementation of the embedding port."""
    if settings.provider.lower() == "ollama":
        # Using Ollama for embeddings
        return OllamaEmbeddingAdapter(
            base_url=settings.ollama.base_url,
            model=settings.ollama.embedding_model,
            fallback_dimension=settings.ollama.vector_dimension
        )


def get_vector_repository() -> VectorRepository:
    """Get the implementation of the vector repository."""
    # Get the embedding port for generating vector embeddings
    embedding_port = get_embedding_port()
    
    # Use Qdrant for vector storage
    return QdrantVectorRepository(
        collection_name=settings.ollama.vector_collection,
        embedding_port=embedding_port
    )


# Application service
def get_chatbot_service() -> ChatbotService:
    """Get the chatbot application service with all its dependencies."""
    # Get all required dependencies
    llm_port = get_llm_port()
    vector_repository = get_vector_repository()
    
    # Create the application service with the dependencies
    return ChatbotService(
        llm_port=llm_port,
        vector_repository=vector_repository,
        top_k=settings.ollama.top_k_documents,
        use_rag=settings.ollama.use_rag
    )


# Driving port (primary) implementation
def get_chatbot_port() -> ChatbotPort:
    """Get the implementation of the chatbot port.
    
    This follows the Hexagonal Architecture pattern by:
    1. Creating the application service with all its dependencies
    2. Creating the primary adapter that implements the port interface
    3. Returning the adapter through the port interface type
    
    External systems only know about the port, not the specific adapter.
    """
    # Get the application service
    chatbot_service = get_chatbot_service()
    
    # Create and return the adapter that implements the port
    return ChatbotAdapter(chatbot_service=chatbot_service)
