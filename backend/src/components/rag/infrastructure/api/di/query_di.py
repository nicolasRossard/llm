"""Dependency injection for query components."""

import logging
from functools import lru_cache

from fastapi import Depends

from src.components.rag.application.handlers.query_handler import QueryHandler
from src.components.rag.application.ports.driven import LLMPort, VectorRetrieverPort, EmbeddingPort
from src.components.rag.application.ports.driven.event_bus_port import EventBusPort
from src.components.rag.config import get_rag_config
from src.components.rag.domain.services.query_service import QueryService
from src.components.rag.infrastructure.adapters.driven.event_bus_adapter import RedisEventBusAdapter
from src.components.rag.infrastructure.adapters.driven.litellm_adapter import LiteLLMAdapter
from src.components.rag.infrastructure.adapters.driven.litellm_embedding_adapter import LiteLLMEmbeddingAdapter
from src.components.rag.infrastructure.persistence.qdrant_vector_retriever_adapter import QdrantVectorRetrieverAdapter

logger = logging.getLogger(__name__)


@lru_cache
def get_vector_retriever() -> VectorRetrieverPort:
    """
    Get the vector retriever implementation.
    
    Returns:
        VectorRetrieverPort: Vector retriever implementation.
    """
    logger.debug("query_di :: Creating vector retriever")
    return QdrantVectorRetrieverAdapter()


@lru_cache
def get_llm() -> LLMPort:
    """
    Get the LLM implementation.
    
    Returns:
        LLMPort: LLM implementation.
    """
    logger.debug("query_di :: Creating LLM adapter")
    return LiteLLMAdapter()


@lru_cache
def get_embedding() -> EmbeddingPort:
    """
    Get the embedding implementation.
    
    Returns:
        EmbeddingPort: Embedding implementation.
    """
    logger.debug("query_di :: Creating embedding adapter")
    return LiteLLMEmbeddingAdapter()


@lru_cache
def get_event_bus() -> EventBusPort:
    """
    Get the event bus implementation.
    
    Returns:
        EventBusPort: Event bus implementation.
    """
    logger.debug("query_di :: Creating event bus adapter")
    return RedisEventBusAdapter(redis_host="rag_event_broker")


@lru_cache
def get_query_service(
    vector_retriever: VectorRetrieverPort = Depends(get_vector_retriever),
    llm: LLMPort = Depends(get_llm),
    embedding: EmbeddingPort = Depends(get_embedding),
    event_bus: EventBusPort = Depends(get_event_bus),
) -> QueryService:
    """
    Get the query service.
    
    Args:
        vector_retriever (VectorRetrieverPort): Vector retriever implementation.
        llm (LLMPort): LLM implementation.
        embedding (EmbeddingPort): Embedding implementation.
        event_bus (EventBusPort): Event bus implementation.
    
    Returns:
        QueryService: Query service instance.
    """
    logger.debug("query_di :: Creating query service")
    return QueryService(
        vector_retriever_port=vector_retriever,
        llm_port=llm,
        embedding_port=embedding,
        rag_config=get_rag_config(),
        event_bus=event_bus,
    )


@lru_cache
def get_query_handler(
    query_service: QueryService = Depends(get_query_service),
    event_bus: EventBusPort = Depends(get_event_bus),
) -> QueryHandler:
    """
    Get the query handler.
    
    Args:
        query_service (QueryService): Query service.
        event_bus (EventBusPort): Event bus implementation.
    
    Returns:
        QueryHandler: Query handler instance.
    """
    logger.debug("query_di :: Creating query handler")
    return QueryHandler(query_service=query_service, event_bus=event_bus)