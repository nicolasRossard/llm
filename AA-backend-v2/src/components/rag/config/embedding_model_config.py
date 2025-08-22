from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EmbeddingModelConfig(BaseSettings):
    """Configuration for embedding models used in the application.
    
    This class defines the configuration parameters required for embedding models,
    including the model name and vector dimensions.
    
    Attributes:
        model_name: The name or identifier of the embedding model to use.
        vector_size: The dimensionality of the embedding vectors produced by the model.
    """
    model_config = SettingsConfigDict(env_prefix='EMBEDDING_', extra="forbid")
    
    model_name: str = Field(
        description="The name or identifier of the embedding model to use"
    )
    vector_size: int = Field(
        description="The dimensionality of the embedding vectors produced by the model"
    )
