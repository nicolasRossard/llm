"""Ollama LLM Adapter implementing the LLMPort interface."""

import json
import logging
import httpx
from typing import List, Dict, Any, Optional

from src.components.chatbot.application.ports.driven import LLMPort
from src.components.chatbot.domain.entities import Message, MessageRole
from src.components.chatbot.domain.value_objects import Response


logger = logging.getLogger(__name__)


class OllamaLLMAdapter(LLMPort):
    """Adapter for Ollama API implementing the LLM Port.
    
    This is a secondary/driven adapter that translates between the application's
    domain model and the external Ollama API.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2:1b"):
        """Initialize the adapter with API connection details.
        
        Args:
            base_url: Ollama API base URL
            model: Model identifier to use (e.g., "llama2", "mistral")
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.client = httpx.AsyncClient(timeout=120.0)  # Extended timeout for LLM responses
        logger.info(f"Initialized Ollama LLM adapter with model {model} at {base_url}")
    
    async def generate_response(self, messages: List[Message]) -> Response:
        """Generate a response using the Ollama API.
        
        Args:
            messages: List of message objects representing the conversation.
            
        Returns:
            Response: The generated response.
        """
        # Convert domain messages to Ollama format
        ollama_messages = []
        for msg in messages:
            role = "user" if msg.role == MessageRole.USER else "assistant" if msg.role == MessageRole.ASSISTANT else "system"
            ollama_messages.append({"role": role, "content": msg.content})
        
        # Prepare request payload
        payload = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 1024,  # Maximum number of tokens to generate
            }
        }
        
        try:
            # Call Ollama API
            url = f"{self.base_url}/api/chat"
            logger.debug(f"Sending request to Ollama API: {url}")
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # Extract content from response
            content = result.get("message", {}).get("content", "")
            
            # Get token usage if available
            input_tokens = result.get("prompt_eval_count", 0)
            output_tokens = result.get("eval_count", 0)
            
            logger.debug(f"Ollama response: {len(content)} chars, {input_tokens} input tokens, {output_tokens} output tokens")
            
            return Response(
                content=content,
                model_used=self.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling Ollama API: {e.response.status_code} {e.response.text}")
            return self._create_error_response(f"HTTP error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Request error calling Ollama API: {str(e)}")
            return self._create_error_response(f"Connection error: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error calling Ollama API: {str(e)}")
            return self._create_error_response(f"Unexpected error: {str(e)}")
    
    def _create_error_response(self, error_msg: str) -> Response:
        """Create an error response when API call fails.
        
        Args:
            error_msg: Error message to include
            
        Returns:
            Response with error information
        """
        return Response(
            content=f"I encountered an issue while processing your request. Technical details: {error_msg}",
            model_used=self.model,
            input_tokens=0,
            output_tokens=0
        )
