import time

from src.components.chatbot.application.ports.driven import LLMPort, EmbeddingPort
from src.components.chatbot.domain.entities import Message, MessageRole
from src.components.chatbot.domain.repositories import VectorRepository
from src.components.chatbot.domain.services.rag_service import RAGService
from src.components.chatbot.domain.value_objects import Query, Response, RAGResponse


class ChatbotService:
    """Application service for processing chat queries using RAG.
    
    This class contains the core business logic for processing chat queries:
    1. Retrieving relevant documents based on the query
    2. Augmenting the query with the retrieved context
    3. Generating a response from the LLM
    4. Formatting the response with citations
    
    This service is used by adapters that implement the ChatbotPort interface.
    """
    
    def __init__(
        self,
        llm_port: LLMPort,
        embedding_port: EmbeddingPort,
        vector_repository: VectorRepository,
        top_k: int = 5,
        use_rag: bool = True,
    ):
        """Initialize the service with its dependencies.
        
        Args:
            llm_port: Port for accessing the LLM service.
            embedding_port: Port for generating text embeddings.
            vector_repository: Repository for vector database operations.
            top_k: Number of documents to retrieve for RAG.
            use_rag: Whether to use RAG or standard LLM generation.
        """
        self.llm_port = llm_port
        self.embedding_port = embedding_port    
        self.vector_repository = vector_repository
        self.top_k = top_k
        self.use_rag = use_rag
        self.rag_service = RAGService(vector_repository, llm_port, embedding_port)
    
    async def process_query(self, query: Query) -> Response | RAGResponse:
        """Process a chat query and generate a response.
        
        Args:
            query: The user's query.
            
        Returns:
            Response: The generated response, with sources if RAG is used.
        """
        start_time = time.time()
        
        if not self.use_rag:
            # Simple LLM generation without RAG
            messages = [
                Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
                Message(role=MessageRole.USER, content=query.content)
            ]
            response = await self.llm_port.generate_response(messages)
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            response.processing_time_ms = processing_time_ms
            
            return response
        
        # RAG flow
        # 1. Retrieve relevant documents
        relevant_docs = self.rag_service.retrieve_relevant_context(query, self.top_k)
        
        # 2. Create augmented prompt with context
        messages = self.rag_service.create_augmented_prompt(query.content, relevant_docs)
        
        # 3. Generate response from LLM
        llm_response = await self.llm_port.generate_response(messages)
        
        # 4. Format response with sources

        # Create RAG response with content and sources
        rag_response = RAGResponse( 
            content=llm_response.content,
            sources=relevant_docs
        )
        
        # Copy metadata from LLM response
        rag_response.model_used = llm_response.model_used
        rag_response.input_tokens = llm_response.input_tokens
        rag_response.output_tokens = llm_response.output_tokens
        
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        rag_response.processing_time_ms = processing_time_ms
        
        return rag_response
