import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
from datetime import datetime, timezone
from src.components.rag.domain.services.query_service import QueryService
from src.components.rag.domain.value_objects import Query, DocumentRetrieval, Message, Response, RAGResponse
from src.components.rag.domain.value_objects.message_role import MessageRole
from src.components.rag.application.ports.driven import VectorRetrieverPort, LLMPort, EmbeddingPort


# filepath: AA-backend-v2/src/components/rag/domain/services/test_query_service.py


@pytest.fixture
def mock_vector_retriever_port():
    mock = AsyncMock(spec=VectorRetrieverPort)
    # Setup the search method to return a list of document retrievals
    doc1 = DocumentRetrieval(
        id=uuid.uuid4(),
        content="Document 1 content",
        metadata={"source": "test_source_1"},
        score=0.95
    )
    doc2 = DocumentRetrieval(
        id=uuid.uuid4(),
        content="Document 2 content",
        metadata={"source": "test_source_2"},
        score=0.85
    )
    mock.search.return_value = [doc1, doc2]
    return mock


@pytest.fixture
def mock_llm_port():
    mock = AsyncMock(spec=LLMPort)
    # Setup the generate_response method to return a Response object
    mock.generate_response.return_value = Response(
        content="This is a test response from the LLM",
        model_used="test-model",
        processing_time_ms=150,
        input_tokens=100,
        output_tokens=50
    )
    return mock


@pytest.fixture
def mock_embedding_port():
    mock = AsyncMock(spec=EmbeddingPort)
    # Setup the embed_text method to return a vector
    mock.embed_text.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
    mock.model = "test-embedding-model"
    mock.fallback_dimension = 5
    return mock


@pytest.fixture
def mock_rag_pipeline():
    mock = AsyncMock()
    # Setup the generate_response method to return a RAGResponse object
    mock.generate_response.return_value = RAGResponse(
        content="This is a test RAG response",
        model_used="test-model",
        processing_time_ms=200,
        input_tokens=120,
        output_tokens=60,
        sources=[
            DocumentRetrieval(
                id=uuid.uuid4(),
                content="Document 1 content",
                metadata={"source": "test_source_1"},
                score=0.95
            )
        ]
    )
    return mock


@pytest.fixture
def mock_rag_config():
    config = MagicMock()
    config.system_prompt = "You are a helpful assistant. Answer based on the provided context."
    return config


@pytest.fixture
def query_service(mock_vector_retriever_port, mock_llm_port, mock_embedding_port, mock_rag_config, mock_rag_pipeline):
    return QueryService(
        vector_retriever_port=mock_vector_retriever_port,
        llm_port=mock_llm_port,
        embedding_port=mock_embedding_port,
        rag_config=mock_rag_config,
        rag_pipeline=mock_rag_pipeline
    )


@pytest.fixture
def sample_query():
    return Query(content="What is the meaning of life?")


@pytest.mark.asyncio
async def test_process_query_happy_path(query_service, sample_query):
    """Test the happy path flow of process_query."""
    # Act
    result = await query_service.process_query(sample_query)

    # Assert
    assert isinstance(result, RAGResponse)
    assert result.content == "This is a test RAG response"
    assert len(result.sources) == 1
    assert result.model_used == "test-model"

    # Verify method calls
    query_service.embedding_port.embed_text.assert_called_once_with(sample_query.content)
    query_service.vector_retriever_port.search.assert_called_once()
    query_service.llm_port.generate_response.assert_called_once()
    query_service.rag_pipeline.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_validate_query_with_empty_content(query_service):
    """Test that _validate_query raises ValueError for empty query content."""
    # Arrange
    empty_query = Query(content="   ")

    # Act & Assert
    with pytest.raises(ValueError, match="Query content cannot be empty"):
        await query_service._validate_query(empty_query)


@pytest.mark.asyncio
async def test_retrieve_relevant_documents(query_service):
    """Test that _retrieve_relevant_documents calls vector_retriever_port.search."""
    # Arrange
    query_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]

    # Act
    documents = await query_service._retrieve_relevant_documents(query_embedding)

    # Assert
    assert len(documents) == 2
    query_service.vector_retriever_port.search.assert_called_once_with(query_embedding)


@pytest.mark.asyncio
async def test_build_context_messages(query_service):
    """Test that _build_context_messages creates the expected message list."""
    # Arrange
    user_query = "What is the meaning of life?"
    doc1 = DocumentRetrieval(
        id=uuid.uuid4(),
        content="Document 1 content",
        metadata={"source": "test_source_1"},
        score=0.95
    )
    doc2 = DocumentRetrieval(
        id=uuid.uuid4(),
        content="Document 2 content",
        metadata={"source": "test_source_2"},
        score=0.85
    )
    retrieved_documents = [doc1, doc2]

    # Act
    messages = await query_service._build_context_messages(user_query, retrieved_documents)

    # Assert
    assert len(messages) == 3
    assert messages[0].role == MessageRole.SYSTEM
    assert messages[0].content == query_service.rag_config.system_prompt
    assert messages[1].role == MessageRole.SYSTEM
    assert "Document 1" in messages[1].content
    assert "Document 2" in messages[1].content
    assert messages[2].role == MessageRole.USER
    assert messages[2].content == user_query


@pytest.mark.asyncio
async def test_process_query_with_embedding_error(query_service, sample_query):
    """Test process_query when embedding_port raises an exception."""
    # Arrange
    query_service.embedding_port.embed_text.side_effect = Exception("Embedding error")

    # Act & Assert
    with pytest.raises(Exception, match="Embedding error"):
        await query_service.process_query(sample_query)


@pytest.mark.asyncio
async def test_process_query_with_vector_retriever_error(query_service, sample_query):
    """Test process_query when vector_retriever_port raises an exception."""
    # Arrange
    query_service.vector_retriever_port.search.side_effect = Exception("Vector retrieval error")

    # Act & Assert
    with pytest.raises(Exception, match="Vector retrieval error"):
        await query_service.process_query(sample_query)


@pytest.mark.asyncio
async def test_process_query_with_llm_error(query_service, sample_query):
    """Test process_query when llm_port raises an exception."""
    # Arrange
    query_service.llm_port.generate_response.side_effect = Exception("LLM error")

    # Act & Assert
    with pytest.raises(Exception, match="LLM error"):
        await query_service.process_query(sample_query)


@pytest.mark.asyncio
async def test_process_query_with_rag_pipeline_error(query_service, sample_query):
    """Test process_query when rag_pipeline raises an exception."""
    # Arrange
    query_service.rag_pipeline.generate_response.side_effect = Exception("RAG pipeline error")

    # Act & Assert
    with pytest.raises(Exception, match="RAG pipeline error"):
        await query_service.process_query(sample_query)


@pytest.mark.asyncio
async def test_process_query_data_flow(query_service, sample_query):
    """Test the complete data flow through process_query."""
    # Act
    await query_service.process_query(sample_query)

    # Assert the flow of data through the service
    # 1. Embedding is created
    query_service.embedding_port.embed_text.assert_called_once_with(sample_query.content)

    # 2. Vector search is performed with the embedding
    embedding = query_service.embedding_port.embed_text.return_value
    query_service.vector_retriever_port.search.assert_called_once_with(embedding)

    # 3. Context messages are built
    # (indirectly tested through the call to llm_port.generate_response)

    # 4. LLM generates a response
    query_service.llm_port.generate_response.assert_called_once()

    # 5. RAG pipeline generates the final response
    llm_response = query_service.llm_port.generate_response.return_value
    retrieved_docs = query_service.vector_retriever_port.search.return_value
    query_service.rag_pipeline.generate_response.assert_called_once_with(
        llm_output=llm_response,
        sources=retrieved_docs
    )