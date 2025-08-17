from src.components.chatbot.application.ports.driving import ChatbotPort
from src.components.chatbot.application.services.chatbot_service import ChatbotService
from src.components.chatbot.domain.value_objects import Query, Response


class ChatbotAdapter(ChatbotPort):
    """Primary adapter implementing the ChatbotPort interface.
    
    This adapter follows the Hexagonal Architecture pattern, serving as the
    boundary between external systems and the application core. It translates
    external requests into calls to the application service.
    
    This is a clear example of a Driving Adapter (Primary Adapter) that conforms
    to a Driving Port (Primary Port).
    """
    
    def __init__(self, chatbot_service: ChatbotService):
        """Initialize the adapter with required dependencies.
        
        Args:
            chatbot_service: The application service that contains the core business logic.
        """
        self.chatbot_service = chatbot_service
    
    async def process_chat_message(self, request: Query) -> Response:
        """Process a chat message by delegating to the ChatbotService.
        
        This method implements the ChatbotPort interface, serving as the entry point
        for external systems into the application core.
        
        Args:
            request: The query object containing the user's message.
            
        Returns:
            Response: The generated response.
        """
        return await self.chatbot_service.process_query(request)
