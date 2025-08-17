from fastapi import APIRouter, Depends, HTTPException

from src.components.chatbot.application.ports.driving import ChatbotPort
from src.components.chatbot.domain.value_objects import Query, Response
from src.components.chatbot.infrastructure.adapters.driving.chatbot_adapter import ChatbotAdapter
from src.components.chatbot.infrastructure.di.container import get_chatbot_port


chabot_rag_router = APIRouter(prefix="/chatbot", tags=["chatbot", "rag"])


@chabot_rag_router.post("/chat", response_model=dict)
async def process_chat_message(
    message: str,
    chatbot_port: ChatbotPort = Depends(get_chatbot_port)
):
    """Process a chat message and return a response.
    
    This endpoint is the entry point for chat interactions, following the
    Hexagonal Architecture pattern. It:
    
    1. Receives the external request (HTTP)
    2. Transforms it into a domain Query object
    3. Passes it to the primary port (ChatbotPort)
    4. Returns the response
    
    The implementation details of how the message is processed are entirely
    hidden behind the ChatbotPort interface.
    """
    try:
        # Convert the message to a domain Query object
        query = Query(content=message)
        
        # Process the query through the port
        response = await chatbot_port.process_chat_message(query)
        
        # Transform the domain response to an API response
        return response.model_dump_json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
