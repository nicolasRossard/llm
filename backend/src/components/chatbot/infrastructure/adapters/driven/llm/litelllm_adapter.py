from typing import Dict, List, Any
import litellm

from src.components.chatbot.application.ports.driven import LLMPort
from src.components.chatbot.infrastructure.adapters.driven.llm.llm_config import LLMConfig


class LiteLLMAdapter(LLMPort):
    def __init__(self, config: LLMConfig):
        self.config = config
        if config.api_key:
            litellm.api_key = config.api_key
        if config.base_url:
            litellm.api_base = config.base_url

    async def generate_response(self, prompt: str, context: List[Dict[str, Any]] = None) -> str:
        messages = []

        # Ajouter le contexte s'il existe
        if context:
            for item in context:
                messages.append({"role": item.get("role", "system"), "content": item.get("content", "")})

        # Ajouter le prompt actuel
        messages.append({"role": "user", "content": prompt})

        response = litellm.completion(
            model=self.config.model_name,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )

        return response.choices[0].message.content
