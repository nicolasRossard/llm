import logging
from typing import Optional

from src.components.rag.application.ports.driven import LLMPort, EmbeddingPort
from src.components.rag.application.services.provider_config_service import ProviderConfigService
from src.components.rag.domain.value_objects import Provider
from src.components.rag.infrastructure.adapters.driven.llm import LiteLLMAdapter, LiteLLMEmbeddingAdapter
from src.components.rag.infrastructure.adapters.driven.ollama.ollama_adapter import OllamaAdapter
from src.components.rag.infrastructure.adapters.driven.ollama.ollama_embedding_adapter import OllamaEmbeddingAdapter

logger = logging.getLogger(__name__)

# Create provider config service instance
provider_config_service = ProviderConfigService()


def get_llm_adapter(provider: Optional[Provider] = None, **overrides) -> LLMPort:
    """Get an LLM adapter for a specified provider with optional overrides."""
    provider = provider or Provider.LITELLM
    config = provider_config_service.get_config_for_provider(provider, **overrides)

    if provider == Provider.LITELLM:
        logger.debug("get_llm_adapter :: Using LiteLLM adapter")
        return LiteLLMAdapter(config)
    elif provider == Provider.OLLAMA:
        logger.debug("get_llm_adapter :: Using Ollama LLM adapter")
        return OllamaAdapter(config)
    else:
        logger.error(f"get_llm_adapter :: Invalid provider specified: {provider}")
        raise ValueError(f"Invalid provider: {provider}")


def get_embedding_adapter(provider: Optional[Provider] = None, **overrides) -> EmbeddingPort:
    """Get an embedding adapter for a specified provider with optional overrides."""
    provider = provider or Provider.LITELLM
    config = provider_config_service.get_config_for_provider(provider, **overrides)

    if provider == Provider.LITELLM:
        logger.debug("get_embedding_adapter :: Using LiteLLM embedding adapter")
        return LiteLLMEmbeddingAdapter(config)
    elif provider == Provider.OLLAMA:
        logger.debug("get_embedding_adapter :: Using Ollama embedding adapter")
        return OllamaEmbeddingAdapter(config)
    else:
        logger.error(f"get_embedding_adapter :: Invalid provider specified: {provider}")
        raise ValueError(f"Invalid provider: {provider}")