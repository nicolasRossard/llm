import time
from typing import Optional

from src.components.rag.application.ports.driven import LLMPort
from src.components.rag.domain.value_objects import Response, Message
from src.components.rag.infrastructure.adapters.driven.litellm_proxy import LiteLLMBaseAdapter, LiteLLMConfig, \
    default_litellm_settings


class LiteLLMAdapter(LiteLLMBaseAdapter, LLMPort):
    """LiteLLM adapter that inherits from LiteLLMBase and implements LLMPort.
    
    Combines base HTTP functionality with the LLMPort interface to provide
    a complete LLM adapter implementation.
    """

    def __init__(self, config: Optional[LiteLLMConfig] = default_litellm_settings):
        """Initialize the LiteLLM adapter.
        
        Args:
            config: Optional LiteLLM configuration. If None, uses default configuration.
        """
        # Initialize base class that handles all configuration
        super().__init__(config)
        self.logger.info("LiteLLMAdapter initialized successfully")
        self.logger.debug(f"Configuration: {self.get_config_summary()}")

    async def _format_response(self, api_response: dict, processing_time_ms: int) -> Response:
        """Format API REST response into domain Response object.

        Args:
            api_response: Response from chat/completions API
            processing_time_ms: Processing time in milliseconds

        Returns:
            Response: Formatted Response object
        """
        self.logger.debug(f"Formatting API response with processing time: {processing_time_ms}ms")
        self.logger.debug(f"API response structure: choices count={len(api_response.get('choices', []))}, "
                         f"usage={api_response.get('usage', {})}")
        
        response = Response(
            content=api_response['choices'][0]['message']['content'],
            model_used=self.config.default_chat_model,
            processing_time_ms=processing_time_ms,
            provider=self.config.provider,
            input_tokens=api_response['usage']['prompt_tokens'],
            output_tokens=api_response['usage']['completion_tokens']
        )
        
        self.logger.debug(f"Formatted response: content_length={len(response.content)}, "
                         f"input_tokens={response.input_tokens}, output_tokens={response.output_tokens}")
        
        return response

    async def generate_response(self, messages: list[Message]) -> Response:
        """Generate response using chat/completions endpoint via LiteLLMBase.
        
        Implementation required by LLMPort interface.

        Args:
            messages: List of conversation messages

        Returns:
            Response: Formatted model response
            
        Raises:
            Exception: If API call fails or response formatting fails
        """
        self.logger.info(f"Starting response generation for {len(messages)} messages")
        self.logger.debug(f"Input messages: {[{'role': m.role, 'content_length': len(m.content)} for m in messages]}")
        
        start = time.time()

        # Convert Message objects to dictionaries
        messages_dict = [
            {"role": message.role, "content": message.content}
            for message in messages
        ]
        self.logger.debug(f"Converted messages to dict format: {len(messages_dict)} messages")

        # Use chat_completion method inherited from LiteLLMBase
        self.logger.info("Calling LiteLLM chat completion endpoint")
        api_response = await self.chat_completion(messages_dict)
        
        end = time.time()
        processing_time_ms = int((end - start) * 1000)
        
        self.logger.info(f"API call completed in {processing_time_ms}ms")
        self.logger.debug(f"API response received: {type(api_response)}")

        # Format API response into domain Response object
        self.logger.info("Formatting API response to domain object")
        response = Response(
            content=api_response['choices'][0]['message']['content'],
            model_used=self.config.default_chat_model,
            processing_time_ms=processing_time_ms,
            provider=self.config.provider,
            input_tokens=api_response['usage']['prompt_tokens'],
            output_tokens=api_response['usage']['completion_tokens']
        )
        
        self.logger.info("Response generation completed successfully")
        self.logger.debug(f"Final response: model={response.model_used}, "
                         f"tokens_in={response.input_tokens}, tokens_out={response.output_tokens}")
        
        return response


if __name__ == "__main__":
    import asyncio


    async def main():
        print("=== Test LiteLLMAdapter (utilisant exclusivement les endpoints HTTP) ===")

        # Test with default config
        adapter = LiteLLMAdapter()
        print("Configuration:", adapter.get_config_summary())

        # Test generate_response method (via HTTP endpoint)
        try:
            response = await adapter.generate_response([
                Message(role="user", content="Hello, how are you?")
            ])
            print("HTTP Endpoint Response:", response)
        except Exception as e:
            print(f"Erreur generate_response: {e}")

        print("\n=== Test LiteLLMBase standalone ===")

        # Test LiteLLMBase only
        llm_base = LiteLLMBaseAdapter()
        try:
            messages = [
                {"role": "user", "content": "Bonjour, comment allez-vous ?"}
            ]

            chat_response = await llm_base.chat_completion(messages)
            print("LiteLLMBase Chat Response:",
                  chat_response.get('choices', [{}])[0].get('message', {}).get('content', 'No content'))

        except Exception as e:
            print(f"Erreur LiteLLMBase: {e}")


    asyncio.run(main())
    time.sleep(3)  # Needed to let the async call finish before the script exits