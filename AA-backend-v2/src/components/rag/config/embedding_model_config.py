from pydantic_settings import BaseSettings, SettingsConfigDict


class EmbeddingModelConfig(BaseSettings):
    """Configuration for embedding models used in the application."""
    model_config = SettingsConfigDict(env_prefix='EMBEDDING_', extra="forbid")
    model_name: str
    vector_size: int
