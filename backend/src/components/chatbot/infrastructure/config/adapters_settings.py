"""Configuration settings for the chatbot component."""

from pydantic_settings import BaseSettings


class OllamaSettings(BaseSettings):
    """Ollama API configuration settings."""

    base_url: str = "http://localhost:11434"

    # Generation settings
    llm_model: str = "llama3.2:1b"
    embedding_model: str = "mxbai-embed-large-v1"  # Can be same or different model

    # Generation parameters
    temperature: float = 0.2
    top_p: float = 0.7
    max_tokens: int = 2048

    # Vector database settings
    vector_collection: str = "documents"
    vector_dimension: int = 1024

    # RAG settings
    top_k_documents: int = 5
    use_rag: bool = True

    class Config:
        """Pydantic configuration."""
        env_prefix = "OLLAMA_"  # Environment variables with OLLAMA_ prefix
        case_sensitive = False


class ChatbotSettings(BaseSettings):
    """Global chatbot configuration settings."""

    # The provider to use (ollama, openai, etc.)
    provider: str = "ollama"

    # Provider-specific settings
    ollama: OllamaSettings = OllamaSettings()

    # API rate limiting
    rate_limit_requests: int = 60  # requests per minute

    class Config:
        """Pydantic configuration."""
        env_prefix = "CHATBOT_"
        case_sensitive = False


class DocumentIngestionSettings(BaseSettings):
    chunk_size: int = 1000
    overlap: int = 200

    class Config:
        """Pydantic configuration."""
        env_prefix = "DOCUMENT_INGESTION_"
        case_sensitive = False


# Create a singleton instance of the settings
chatbot_settings = ChatbotSettings()
document_ingestion_settings = DocumentIngestionSettings()
