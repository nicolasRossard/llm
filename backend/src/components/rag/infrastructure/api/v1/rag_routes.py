import logging

from fastapi import APIRouter, Depends, HTTPException

from src.components.rag.application.handlers.query_handler import QueryHandler
from src.components.rag.domain.services.query_service import QueryService
from src.components.rag.domain.value_objects import Query, RAGResponse
from src.components.rag.config import RAGConfig
from src.components.rag.infrastructure.adapters.driven.llm import LiteLLMAdapter
from src.components.rag.infrastructure.adapters.driven.llm.litellm_embedding_adapter import LiteLLMEmbeddingAdapter

from src.components.rag.infrastructure.api.v1.dto import response_to_dto
from src.components.rag.infrastructure.persistence.qdrant_vector_retriever_adapter import QdrantVectorRetrieverAdapter

# Create a router for RAG endpoints
rag_router = APIRouter(prefix="/rag", tags=["rag"])

# Setup logging
logger = logging.getLogger(__name__)


async def get_query_handler() -> QueryHandler:
    """
    Factory function to create and configure the QueryHandler with all dependencies.
    
    Returns:
        QueryHandler: Configured query handler with all necessary dependencies.
    """
    logger.info("get_query_handler :: Creating query handler dependencies")
    
    # Initialize configuration
    rag_config = RAGConfig(
        system_prompt="You are a helpful assistant that provides accurate information based on the provided context. If the context does not contain the answer, respond with 'I don't know'.",
    )
    
    # Initialize adapters
    llm_adapter = LiteLLMAdapter()
    embedding_adapter = LiteLLMEmbeddingAdapter()
    vector_retrieve_adapter = QdrantVectorRetrieverAdapter()
    
    # Initialize service
    query_service = QueryService(
        vector_retriever_port=vector_retrieve_adapter,
        llm_port=llm_adapter,
        embedding_port=embedding_adapter,
        rag_config=rag_config
    )
    
    # Initialize handler
    query_handler = QueryHandler(query_service=query_service)
    
    logger.info("get_query_handler :: Query handler successfully created")
    return query_handler


@rag_router.post("/chat", response_model=RAGResponse)
async def chat(request: str, handler: QueryHandler = Depends(get_query_handler)) -> dict:
    """
    Process a user query through the RAG system.
    
    Args:
        request: The query request containing the user's question.
        handler: The query handler dependency.
    
    Returns:
        RAGResponse: Response containing the generated answer and source documents.
    
    Raises:
        HTTPException: If an error occurs during query processing.
    """
    logger.info("chat :: Processing new chat request")

    try:
        # Create domain query object from request
        query = Query(content=request)
        
        # Process the query
        response = await handler.query(query)
        
        logger.info("chat :: Query processed successfully")
        return await response_to_dto(response)
        
    except ValueError as e:
        logger.error(f"chat :: Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"chat :: Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your query")