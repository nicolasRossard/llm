import time
from typing import Optional

from src.components.chatbot.application.ports.driven import LLMPort, EmbeddingPort
from src.components.chatbot.application.services.chatbot_service import ChatbotService
from src.components.chatbot.domain.repositories import VectorRepository
from src.components.chatbot.domain.value_objects import Query, Response


class ProcessChatQuery:
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
        llm_port: LLMPort,
        embedding_port: EmbeddingPort,
        vector_repository: VectorRepository,
        top_k: int = 5,
        use_rag: bool = True,
    ):
        """Initialize the use case with its dependencies.
        
        Args:
            llm_port: Port for accessing the LLM service.
            embedding_port: Port for generating text embeddings.
            vector_repository: Repository for vector database operations.
            top_k: Number of documents to retrieve for RAG.
            use_rag: Whether to use RAG or standard LLM generation.
        """
        self.service = ChatbotService(
            llm_port=llm_port,
            embedding_port=embedding_port,
            vector_repository=vector_repository,
            top_k=top_k,
            use_rag=use_rag
        )
    
    async def execute(self, query: Query) -> Response:
        """Execute the complete chat query processing.
        
        This method is maintained for backward compatibility.
        It delegates to the ChatbotService.process_query method.
        
        Args:
            query: The user's query.
            
        Returns:
            Response: The generated response, with sources if RAG is used.
        """
        return await self.service.process_query(query)
