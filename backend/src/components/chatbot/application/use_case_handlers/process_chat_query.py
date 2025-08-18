from src.components.chatbot.application.ports.driving import ChatbotPort
from src.components.chatbot.domain.value_objects import Query, Response


class ProcessChatQuery(ChatbotPort):
    """Application use case for processing a chat query using RAG.
    
    This class is maintained for backward compatibility.
    It delegates to the ChatbotService for actual implementation.
    
    In accordance with hexagonal architecture principles, this class has been
    refactored into:
    1. ChatbotService (application service with business logic)
    2. ChatbotAdapter (adapter implementing the driving port)
    """
    
    def __init__(
        self,
        chatbot_service
    ):
        """Initialize the use case with its dependencies.

        Args:
            chatbot_service: An instance of ChatbotService that handles the chat query processing.
        """
        self.chatbot_service = chatbot_service
    
    async def process_chat_message(self, query: Query) -> Response:
        """Execute the complete chat query processing.
        
        This method is maintained for backward compatibility.
        It delegates to the ChatbotService.process_query method.
        
        Args:
            query: The user's query.
            
        Returns:
            Response: The generated response, with sources if RAG is used.
        """
        return await self.chatbot_service.process_query(query)
