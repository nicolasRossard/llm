from pydantic_settings import BaseSettings, SettingsConfigDict

from src.components.rag.config import EmbeddingModelConfig


class VectorRepositoryConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='VECTOR_REPO_', extra="forbid")
    embedding_model_config: EmbeddingModelConfig
    distance_type: str
    top_k: int
    collection_name: str | None = None
