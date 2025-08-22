from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.components.rag.config import EmbeddingModelConfig


class VectorRepositoryConfig(BaseSettings):
    """Configuration for vector repository settings.
    
    This class defines the configuration parameters for vector repositories
    used in RAG (Retrieval-Augmented Generation) systems.
    
    Attributes:
        embedding_model_config: Configuration for the embedding model used to vectorize documents.
        distance_type: The distance metric used for vector similarity calculations.
        top_k: The number of top similar vectors to retrieve during search.
        collection_name: Optional name of the vector collection to use.
    """
    
    model_config = SettingsConfigDict(env_prefix='VECTOR_REPO_', extra="forbid")
    
    embedding_model_config: EmbeddingModelConfig = Field(
        description="Configuration for the embedding model used to vectorize documents"
    )
    distance_type: str = Field(
        description="The distance metric used for vector similarity calculations (e.g., 'cosine', 'euclidean')"
    )
    top_k: int = Field(
        description="The number of top similar vectors to retrieve during search operations"
    )
    collection_name: str | None = Field(
        default=None,
        description="Optional name of the vector collection to use for storage and retrieval"
    )
