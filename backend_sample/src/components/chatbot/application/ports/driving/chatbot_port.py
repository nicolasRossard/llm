from abc import ABC, abstractmethod


from src.components.chatbot.domain.value_objects import Query, Response


class ChatbotPort(ABC):
    """
    Driven port for chatbot interactions
    Defines the interface for external systems to interact with the chatbot
    This is the main entry point for chat functionality
    """

    @abstractmethod
    async def process_chat_message(self, request: Query) -> Response:
        """
        Processes a chat message and returns a response
        Main use case for chat interactions
        """
        pass
