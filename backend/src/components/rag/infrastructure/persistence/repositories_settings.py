from pydantic import Field
from pydantic_settings import BaseSettings


class RepositorySettings(BaseSettings):
    """
    Qdrant API configuration settings.

    Contains connection parameters and configuration for Qdrant vector database.
    """

    base_url: str = Field(
        "localhost",
        description="Base URL for the Qdrant server"
    )
    grpc_port: int = Field(
        6334,
        description="Port for gRPC connection to Qdrant"
    )
    http_port: int = Field(
        6333,
        description="Port for HTTP connection to Qdrant"
    )

    # Generation settings
    collection_name: str = Field(
        "documents",
        description="Name of the collection to store documents"
    )
    fallback_dimension: int = Field(
        768,
        description="Default vector dimension (nomic-embed-text-v1.5 dimension)"
    )

    class Config:
        """Pydantic configuration for environment variables."""
        env_prefix = "QDRANT_"  # Environment variables with QDRANT_ prefix
        case_sensitive = False


repo_settings = RepositorySettings()
