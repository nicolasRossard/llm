from typing import List

from src.components.chatbot.application.ports.driven import LLMPort
from src.components.chatbot.domain.entities import Message, MessageRole
from src.components.chatbot.domain.repositories import VectorRepository
from src.components.chatbot.domain.value_objects import Query, DocumentRetrieval, RAGResponse


class RAGService:
    """Domain service to handle the core RAG (Retrieval Augmented Generation) process.
    
    This service coordinates the retrieval of relevant documents based on a query
    and prepares them for use by the LLM.
    """
    
    def __init__(self, vector_repository: VectorRepository, llm_port: LLMPort):
        """Initialize the service with required dependencies.
        
        Args:
            vector_repository: Repository for accessing the vector database.
        """
        self.vector_repository = vector_repository
        self.llm_port = llm_port
    
    async def retrieve_relevant_context(self, query: Query, top_k: int = 5) -> List[DocumentRetrieval]:
        """Retrieve the most relevant documents for a given query.
        
        Args:
            query: The user query to search for relevant documents.
            top_k: Maximum number of documents to retrieve.
            
        Returns:
            List of relevant documents.
        """
        # Use the vector repository to perform semantic search
        relevant_docs = await self.vector_repository.search(query, top_k=top_k)
        return relevant_docs
    
    async def create_augmented_prompt(self, query: str, documents: List[DocumentRetrieval]) -> List[Message]:
        """Create a prompt with retrieved context for the LLM.
        
        Args:
            query: The original user query.
            documents: Retrieved relevant documents.
            
        Returns:
            List of messages to send to the LLM.
        """
        # Create a system message with context
        context_str = "\n\n".join([f"Document {i+1}:\n{doc.content}" for i, doc in enumerate(documents)])
        
        system_content = (
            "You are a helpful assistant that answers questions based on the provided context. "
            "If the answer is not in the context, say that you don't know instead of making up information. "
            "Use the following retrieved documents to answer the user's question:\n\n"
            f"{context_str}"
        )
        
        # Create the message list
        messages = [
            Message(role=MessageRole.SYSTEM, content=system_content),
            Message(role=MessageRole.USER, content=query)
        ]
        
        return messages
