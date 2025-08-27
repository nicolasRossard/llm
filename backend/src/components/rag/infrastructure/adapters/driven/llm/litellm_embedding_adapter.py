import time
from typing import Optional

from src.components.rag.application.ports.driven import EmbeddingPort
from src.components.rag.domain.value_objects import Embedding
from src.components.rag.infrastructure.adapters.driven.litellm_proxy import LiteLLMBaseAdapter
from src.components.rag.infrastructure.adapters.driven.litellm_proxy import LiteLLMConfig, \
    default_litellm_settings


class LiteLLMEmbeddingAdapter(LiteLLMBaseAdapter, EmbeddingPort):
    """LiteLLM adapter that inherits from LiteLLMBase and implements LLMPort.

    Combines base HTTP functionality with the LLMPort interface to provide
    a complete LLM adapter implementation.
    """

    def __init__(self, config: LiteLLMConfig = default_litellm_settings):
        """Initialize the LiteLLM adapter.

        Args:
            config: Optional LiteLLM configuration. If None, uses default configuration.
        """
        # Initialize base class that handles all configuration
        super().__init__(config)
        self.logger.info("LiteLLMAdapter initialized successfully")
        self.logger.debug(f"Configuration: {self.get_config_summary()}")

    async def _format_response(self, api_response: dict, processing_time_ms: int) -> Embedding:
        """Format API REST response into domain Response object.

        Args:
            api_response: Response from chat/completions API
            processing_time_ms: Processing time in milliseconds

        Returns:
            Response: Formatted Response object
        """
        self.logger.debug(f"_format_response :: Formatting API response with processing time: {processing_time_ms}ms")
        self.logger.debug(
            f"_format_response :: API response structure: data count={len(api_response.get('data', []))}, "
            f"usage={api_response.get('usage', {})}")

        response = Embedding(
            model=api_response['model'],
            vector=api_response['data'][0]['embedding'],
            prompt_tokens=api_response['usage'].get('prompt_tokens'),
            completion_tokens=api_response['usage'].get('completion_tokens'),
            provider=self.config.provider,
            processing_time_ms=processing_time_ms
        )

        return response

    async def embed_text(self, text: str, model: str = None) -> Embedding:
        """
        Generate an embedding for the provided text.

        Args:
            text (str): The text to embed.
            model (str, optional): The embedding model to use. Defaults to config model if None.

        Returns:
            Embedding: The embedding value object containing the vector and metadata.
        """
        self.logger.info(f"embed_text :: Generating embedding for text of length {len(text)}")

        start = time.time()
        api_response = await self.embeddings(input_text=text, model=model)
        end = time.time()
        processing_time_ms = int((end - start) * 1000)

        self.logger.debug(f"embed_text :: API response received in {processing_time_ms}ms")

        return await self._format_response(api_response, processing_time_ms)


if __name__ == "__main__":
    import asyncio


    async def main():
        print("=== Test LiteLLMAdapter (utilisant exclusivement les endpoints HTTP) ===")

        # Test avec la configuration par défaut
        adapter = LiteLLMEmbeddingAdapter()
        print("Configuration:", adapter.get_config_summary())

        # Test de la méthode generate_response (via endpoint HTTP)
        try:
            response = await adapter.embed_text("sentence to embed")
            print("HTTP Endpoint Response:", response)
        except Exception as e:
            print(f"Erreur generate_response: {e}")


    asyncio.run(main())
    time.sleep(3)  # Needed to let the async call finish before the script exits