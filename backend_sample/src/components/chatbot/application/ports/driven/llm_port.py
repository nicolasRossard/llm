from abc import ABC, abstractmethod
from typing import List
from src.components.chatbot.domain.entities import Message
from src.components.chatbot.domain.value_objects import Response


class LLMPort(ABC):
    """Port interface for text generation using a Large Language Model."""

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Message]
    ) -> Response:
        """Generate a text response from the LLM.

        Args:
            messages: List of messages in conversation format.

        Returns:
            Response: The generated response with metadata.
        """
        pass
