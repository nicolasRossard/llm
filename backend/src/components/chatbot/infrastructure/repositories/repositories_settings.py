from pydantic_settings import BaseSettings


class RepositorySettings(BaseSettings):
    """Qdrant API configuration settings."""
    
    base_url: str = "localhost"
    grpc_port: int = 6334
    http_port: int = 6333
    
    # Generation settings
    collection_name: str = "documents"

    class Config:
        """Pydantic configuration."""
        env_prefix = "QDRANT"  # Environment variables with QDRANT_ prefix
        case_sensitive = False

repo_settings = RepositorySettings()
