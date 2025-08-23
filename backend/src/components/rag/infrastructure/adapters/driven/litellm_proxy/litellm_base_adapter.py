import logging
from typing import Optional

from .litellm_config import LiteLLMConfig, default_litellm_settings


class LiteLLMBaseAdapter:
    """Base class for LiteLLM calls with chat/completions and embeddings endpoint management.
    
    This class provides a unified interface for making requests to LiteLLM endpoints,
    handling both chat completions and embeddings. It manages authentication,
    error handling, and request configuration.
    """

    def __init__(self, config: Optional[LiteLLMConfig] = default_litellm_settings):
        """Initialize the class with provided configuration or use default configuration.

        Args:
            config: LiteLLM configuration. If None, uses load_litellm_config().
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("__init__ :: Initializing LiteLLMBase")
        
        self.config = config
        self.logger.debug(f"__init__ :: Using configuration: {self.config.model_dump()}")

        # Configure litellm proxy using the provided config
        self.default_litellm_chat_model = f"{self.config.provider}/{self.config.default_chat_model}"
        self.default_litellm_embedding_model = f"{self.config.provider}/{self.config.default_embedding_model}"
        
        self.logger.debug(f"__init__ :: Default chat model: {self.default_litellm_chat_model}")
        self.logger.debug(f"__init__ :: Default embedding model: {self.default_litellm_embedding_model}")

        # Common authentication headers
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }
        self.logger.debug("__init__ :: Authentication headers configured")
        self.logger.info("__init__ :: LiteLLMBase initialization completed")

    async def _make_request(self, endpoint: str, payload: dict) -> dict:
        """Make an HTTP request to the specified endpoint.

        Args:
            endpoint: The API endpoint (e.g., "chat/completions", "embeddings").
            payload: The data to send in the request body.

        Returns:
            dict: Dictionary containing the API response.

        Raises:
            httpx.RequestError: If there's a request error.
            httpx.HTTPStatusError: If there's an HTTP error.
        """
        import httpx
        
        url = f"{self.config.base_url.rstrip('/')}/{endpoint}"
        self.logger.info(f"_make_request :: Making request to endpoint: {endpoint}")
        self.logger.debug(f"_make_request :: Request URL: {url}")
        self.logger.debug(f"_make_request :: Request payload: {payload}")

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            try:
                self.logger.debug(f"_make_request :: Sending POST request with timeout: {self.config.timeout}s")
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                
                response_data = response.json()
                self.logger.info(f"_make_request :: Request to {endpoint} completed successfully")
                self.logger.debug(f"_make_request :: Response status: {response.status_code}")
                self.logger.debug(f"_make_request :: Response data: {response_data}")
                
                return response_data
                
            except httpx.RequestError as e:
                self.logger.error(f"_make_request :: Request error for {url}: {e}")
                raise httpx.RequestError(f"Request error for {url}: {e}")
            except httpx.HTTPStatusError as e:
                error_detail = ""
                try:
                    error_detail = response.json()
                except:
                    error_detail = response.text
                    
                self.logger.error(f"_make_request :: HTTP error {response.status_code} for {url}: {error_detail}")
                raise

    async def chat_completion(
            self,
            messages: list[dict[str, str]],
            model: Optional[str] = None,
            temperature: Optional[float] = None,
            max_tokens: Optional[int] = None,
            **kwargs
    ) -> dict:
        """Generate chat completion for the given messages.

        Args:
            messages: List of conversation messages.
            model: Model to use (default: config.default_chat_model).
            temperature: Generation temperature (default: config.temperature).
            max_tokens: Maximum number of tokens (default: config.max_tokens).
            **kwargs: Additional arguments for the API.

        Returns:
            dict: Dictionary containing the chat/completions API response.
        """
        self.logger.info("chat_completion :: Starting chat completion request")
        
        model_to_use = model or self.default_litellm_chat_model
        temp_to_use = temperature or self.config.temperature
        tokens_to_use = max_tokens or self.config.max_tokens
        
        self.logger.debug(f"chat_completion :: Using model: {model_to_use}")
        self.logger.debug(f"chat_completion :: Using temperature: {temp_to_use}")
        self.logger.debug(f"chat_completion :: Using max_tokens: {tokens_to_use}")
        self.logger.debug(f"chat_completion :: Messages count: {len(messages)}")
        
        payload = {
            "model": model_to_use,
            "messages": messages,
            "temperature": temp_to_use,
            "max_tokens": tokens_to_use,
            **kwargs
        }

        result = await self._make_request("chat/completions", payload)
        self.logger.info("chat_completion :: Chat completion request completed")
        return result
    
    async def embeddings(self, input_text, model: Optional[str] = None, **kwargs) -> dict:
        """Generate embeddings for the given input text.

        Args:
            input_text: Text or list of texts to transform into embeddings.
            model: Embedding model to use (default: config.default_embedding_model).
            **kwargs: Additional arguments for the API.

        Returns:
            dict: Dictionary containing the embeddings API response.
        """
        payload = {
            "model": model or self.default_litellm_embedding_model,
            "input": input_text,
            **kwargs
        }

        return await self._make_request("embeddings", payload)

    def get_config_summary(self) -> dict:
        """Return a summary of the current configuration.

        Returns:
            dict: Dictionary with configuration parameters.
        """
        return {
            "base_url": self.config.base_url,
            "api_key": f"{self.config.api_key[:8]}..." if self.config.api_key and len(
                self.config.api_key) > 8 else "***",
            "timeout": self.config.timeout,
            "default_chat_model": self.config.default_chat_model,
            "default_embedding_model": self.config.default_embedding_model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "provider": self.config.provider
        }
