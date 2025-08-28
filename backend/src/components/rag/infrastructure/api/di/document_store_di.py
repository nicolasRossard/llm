import logging

from src.components.rag.application.handlers.document_store_handler import DocumentStoreHandler
from src.components.rag.application.handlers.query_handler import QueryHandler
from src.components.rag.application.ports.driven import EmbeddingPort, VectorStorePort
from src.components.rag.application.ports.driven.text_chunking_port import TextChunkingPort
from src.components.rag.application.ports.driven.text_extraction_port import TextExtractionPort
from src.components.rag.domain.services.document_store_service import DocumentStoreService
from src.components.rag.config import RAGConfig
from src.components.rag.infrastructure.adapters.driven import \
    DoclingTextExtractionAdapter

from src.components.rag.infrastructure.adapters.driven import DoclingTextChunkingAdapter
from src.components.rag.infrastructure.adapters.driven.llm.litellm_embedding_adapter import LiteLLMEmbeddingAdapter
from src.components.rag.infrastructure.persistence import QdrantVectorStoreAdapter

from src.components.rag.infrastructure.persistence.qdrant_vector_retriever_adapter import QdrantVectorRetrieverAdapter

# Setup logging
logger = logging.getLogger(__name__)


def get_document_store_handler():
    """
    Create and configure a DocumentStoreHandler with all required dependencies.

    Returns:
        DocumentStoreHandler: Configured handler for document store operations.
    """
    logger.info("get_document_store_handler :: Starting handler initialization")

    # Initialize configuration
    logger.debug("get_document_store_handler :: Initializing RAG configuration")
    rag_config = RAGConfig(
        system_prompt="You are a helpful assistant that provides accurate information based on the provided context. If the context does not contain the answer, respond with 'I don't know'.",
    )

    # Initialize adapters
    logger.debug("get_document_store_handler :: Initializing adapters")
    embedding_adapter: EmbeddingPort = LiteLLMEmbeddingAdapter()
    vector_store: VectorStorePort = QdrantVectorStoreAdapter()
    text_extraction_port: TextExtractionPort = DoclingTextExtractionAdapter()
    text_chunking_port: TextChunkingPort = DoclingTextChunkingAdapter()
    
    # Initialize service
    logger.debug("get_document_store_handler :: Initializing document store service")
    document_store_service = DocumentStoreService(
        vector_store_port=vector_store,
        embedding_port=embedding_adapter,
        text_extraction_port=text_extraction_port,
        text_chunking_port=text_chunking_port
    )

    # Initialize handler
    logger.debug("get_document_store_handler :: Initializing document store handler")
    document_store_handler: DocumentStoreHandler = DocumentStoreHandler(document_store_service=document_store_service)

    logger.info("get_document_store_handler :: Handler initialization completed")
    return document_store_handler