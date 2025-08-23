import logging

from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings


class LiteLLMConfig(BaseSettings):
    """Configuration for LiteLLM adapter.

    This class defines the configuration parameters needed to connect to LiteLLM,
    which provides a unified interface for various language model providers.
    It handles both chat completion and embedding model configurations.

    Attributes:
        api_key: The API key for authentication with the LLM provider.
        base_url: The base URL for the LLM API endpoint.
        provider: The LLM provider identifier for LiteLLM's unified interface.
        timeout: Request timeout in seconds.
        default_chat_model: The chat model name to use for completions.
        default_embedding_model: The default embedding model name to use for embeddings.
        temperature: Temperature parameter for text generation (0.0 to 2.0).
        max_tokens: Maximum number of tokens to generate in responses.
    """

    model_config = SettingsConfigDict(
        env_prefix="LITELLM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra='ignore',
    )

    api_key: str = Field(description="API key for authentication with the LLM provider")
    base_url: str = Field(default="http://localhost:4000", description="Base URL for the LLM API endpoint")
    provider: str = Field(default="ollama", description="LLM provider identifier for LiteLLM's unified interface")
    default_chat_model: str = Field(default="llama3.2:1b", description="The chat model name to use for completions",
                                    alias="chat_model")
    default_embedding_model: str = Field(default="nomic-embed-text:v1.5",
                                         description="The embedding model name to use for embeddings",
                                         alias="embedding_model")
    timeout: float = Field(default=30, description="Request timeout in seconds")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0,
                               description="Temperature parameter for text generation (0.0 to 2.0)")
    max_tokens: int = Field(default=2048, gt=0, description="Maximum number of tokens to generate in responses")


def load_litellm_config() -> LiteLLMConfig:
    """Load LiteLLM configuration from environment variables and .env file.

    This function creates a LiteLLMConfig instance that automatically loads
    values from environment variables with LITELLM_ prefix and from .env file.

    Returns:
        LiteLLMConfig: Instance of LiteLLMConfig with values from environment variables and .env file.

    Raises:
        ValueError: If required configuration values are missing or invalid.
    """
    logger = logging.getLogger(__name__)
    logger.info("load_litellm_config :: Loading LiteLLM configuration")

    config = LiteLLMConfig()

    logger.debug(
        f"load_litellm_config :: Configuration loaded: {dict((k, v if k != 'api_key' else '***' if v else '') for k, v in config.model_dump().items())}")

    return config


default_litellm_settings = load_litellm_config()

if __name__ == "__main__":
    # For testing purposes, print the loaded configuration (excluding sensitive info)
    config = load_litellm_config()
    print(config.model_dump(exclude={"api_key"}))