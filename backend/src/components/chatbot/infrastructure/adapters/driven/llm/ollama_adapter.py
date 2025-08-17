from typing import Any, List, Dict
import requests

from src.components.chatbot.application.ports.driven import LLMPort
from src.components.chatbot.infrastructure.adapters.driven.llm.llm_config import LLMConfig


class OllamaAdapter(LLMPort):
    def __init__(self, config: LLMConfig):
        self.config = config
        self.base_url = config.base_url or "http://localhost:11434/api"

    async def generate_response(self, prompt: str, context: List[Dict[str, Any]] = None) -> str:
        url = f"{self.base_url}/generate"

        # Formatage du contexte pour Ollama
        formatted_context = ""
        if context:
            for item in context:
                role = item.get("role", "system")
                content = item.get("content", "")
                formatted_context += f"<{role}>{content}</{role}>\n"

        data = {
            "model": self.config.model_name,
            "prompt": formatted_context + prompt,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }

        response = requests.post(url, json=data)
        response_json = response.json()

        return response_json.get("response", "")
