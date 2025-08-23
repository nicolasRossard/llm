from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RAGConfig(BaseSettings):
    """Configuration settings for RAG (Retrieval-Augmented Generation) system.

    This class defines the configuration parameters needed for the RAG system,
    including system prompts and other related settings.

    Attributes:
        system_prompt: The system prompt used to guide the RAG model's behavior.
    """

    model_config = SettingsConfigDict(env_prefix='RAG_', extra="forbid")

    system_prompt: str = Field(
        description="The system prompt that defines the behavior and context for the RAG model"
    )
    