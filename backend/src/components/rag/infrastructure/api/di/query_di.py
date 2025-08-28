import logging


from src.components.rag.application.handlers.query_handler import QueryHandler
from src.components.rag.domain.services.query_service import QueryService
from src.components.rag.config import RAGConfig
from src.components.rag.infrastructure.adapters.driven.llm import LiteLLMAdapter
from src.components.rag.infrastructure.adapters.driven.llm.litellm_embedding_adapter import LiteLLMEmbeddingAdapter

from src.components.rag.infrastructure.persistence.qdrant_vector_retriever_adapter import QdrantVectorRetrieverAdapter

# Setup logging
logger = logging.getLogger(__name__)


def get_query_handler() -> QueryHandler:
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