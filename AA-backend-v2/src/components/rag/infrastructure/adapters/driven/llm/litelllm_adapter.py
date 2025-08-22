import os
import time

from pydantic import Field
import litellm
from litellm import ModelResponse
from src.components.rag.application.ports.driven import LLMPort
from src.components.rag.config import LLMModelConfig
from src.components.rag.config.settings import settings
from src.components.rag.domain.value_objects import Response, Message


class LiteLLMConfig(LLMModelConfig):
    """Configuration for LiteLLM adapter.

    This class defines the configuration parameters needed to connect to LiteLLM,
    which provides a unified interface for various language model providers.

    Attributes:
        api_key: The API key for authentication with the LLM provider.
            If None, the adapter will attempt to use environment variables
            or default authentication methods.
        base_url: The base URL for the LLM API endpoint. If None, the default
            provider endpoint will be used.
        provider: The LLM provider identifier. Defaults to "litellm" for
            LiteLLM's unified interface.
    """

    api_key: str | None = Field(
        default=None,
        description="API key for authentication with the LLM provider"
    )
    base_url: str | None = Field(
        default=None,
        description="Base URL for the LLM API endpoint"
    )
    provider: str = Field(
        default="litellm",
        description="LLM provider identifier for LiteLLM's unified interface"
    )
    api_key: str | None = Field(default=None)
    base_url: str | None = Field(default=None)
    provider: str = Field(default="litellm")


litellm_config = LiteLLMConfig(
    **settings.llm.model_dump(exclude="model_name") |
      {
          "api_key": os.getenv("LLM_LITELLM_API_KEY"),
          "base_url": os.getenv("LLM_LITELLM_BASE_URL"),
          "model_name": os.getenv("LLM_LITELLM_MODEL_NAME", f"ollama/{settings.llm.model_name}"),
          "provider": "litellm/ollama"
      }
)


class LiteLLMAdapter(LLMPort):

    def __init__(self, config: LiteLLMConfig):
        self.config = config
        if self.config.api_key:
            litellm.api_key = self.config.api_key
        if self.config.base_url:
            litellm.api_base = self.config.base_url

    async def _format_response(self, response: ModelResponse, processing_time_ms: int) -> Response:
        return Response(
            content=response.choices[0].message.content,
            model_used=self.config.model_name,
            processing_time_ms=processing_time_ms,
            provider=self.config.provider,  # Litellm as proxy and get the provider by model_name
            input_tokens=response['usage'].prompt_tokens,
            output_tokens=response['usage'].completion_tokens
        )

    async def generate_response(self, messages: list[Message]) -> Response:
        start = time.time()
        response = litellm.completion(
            model=self.config.model_name,
            messages=[
                {
                    "role": message.role,
                    "content": message.content
                } for message in messages
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        end = time.time()
        processing_time_ms = int((end - start) * 1000)
        return await self._format_response(response, processing_time_ms)


if __name__ == "__main__":
    adapter = LiteLLMAdapter(litellm_config)
    import asyncio


    async def main():
        response = await adapter.generate_response([
            Message(role="user", content="Hello, how are you?")
        ])
        print(response)


    asyncio.run(main())
    time.sleep(2)  # Needed to let the async call finish before the script exits
