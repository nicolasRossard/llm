import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

from src.components.rag.domain.services.query_service import QueryService
from src.components.rag.domain.value_objects import Query, DocumentRetrieval, Message, Response, RAGResponse, Embedding
from src.components.rag.domain.value_objects.message_role import MessageRole
from src.components.rag.application.ports.driven import VectorRetrieverPort, LLMPort, EmbeddingPort
import unittest


class TestQueryService(unittest.TestCase):
    """
    Test cases for QueryService.
    
    These tests focus on verifying the behavior of QueryService while mocking
    external dependencies to ensure isolated testing.
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock ports
        self.mock_vector_retriever_port = AsyncMock(spec=VectorRetrieverPort)
        self.mock_llm_port = AsyncMock(spec=LLMPort)
        self.mock_embedding_port = AsyncMock(spec=EmbeddingPort)
        
        # Create mock config
        self.mock_rag_config = MagicMock()
        self.mock_rag_config.system_prompt = "You are a helpful assistant. Answer based on the provided context."
        
        # Sample documents for testing
        self.doc1 = DocumentRetrieval(
            id=uuid.uuid4(),
            content="Document 1 content",
            metadata={"source": "test_source_1"},
            score=0.95
        )
        self.doc2 = DocumentRetrieval(
            id=uuid.uuid4(),
            content="Document 2 content",
            metadata={"source": "test_source_2"},
            score=0.85
        )
        
        # Setup default mock returns
        self.mock_vector_retriever_port.search.return_value = [self.doc1, self.doc2]
        
        self.mock_llm_port.generate_response.return_value = Response(
            content="This is a test response from the LLM",
            model_used="test-model",
            processing_time_ms=150,
            input_tokens=100,
            output_tokens=50
        )
        
        self.mock_embedding_port.embed_text.return_value = Embedding(
            model="text-embedding-ada-002",
            embedding=[0.1, 0.2, 0.3, 0.4, 0.5],
            prompt_tokens=10,
            completion_tokens=0,
            provider="openai"
        )
        
        # Sample query
        self.sample_query = Query(content="What is the meaning of life?")
        
        # Initialize service
        self.query_service = QueryService(
            vector_retriever_port=self.mock_vector_retriever_port,
            llm_port=self.mock_llm_port,
            embedding_port=self.mock_embedding_port,
            rag_config=self.mock_rag_config,
        )

    @pytest.mark.asyncio
    async def test_process_query_happy_path(self):
        """Test the happy path flow of process_query."""
        # Act
        result = await self.query_service.process_query(self.sample_query)

        # Assert
        self.assertIsInstance(result, RAGResponse)
        self.assertEqual(result.content, "This is a test response from the LLM")
        self.assertEqual(len(result.sources), 2)
        self.assertEqual(result.model_used, "test-model")
        self.assertEqual(result.processing_time_ms, 150)
        self.assertEqual(result.input_tokens, 100)
        self.assertEqual(result.output_tokens, 50)

        # Verify method calls
        self.mock_embedding_port.embed_text.assert_called_once_with(self.sample_query.content)
        self.mock_vector_retriever_port.search.assert_called_once()
        self.mock_llm_port.generate_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_query_with_empty_content(self):
        """Test that _validate_query raises ValueError for empty query content."""
        # Arrange
        empty_query = Query(content="   ")

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            await self.query_service._validate_query(empty_query)
        
        self.assertIn("Query content cannot be empty", str(context.exception))

    @pytest.mark.asyncio
    async def test_validate_query_with_valid_content(self):
        """Test that _validate_query returns the query for valid content."""
        # Act
        result = await self.query_service._validate_query(self.sample_query)

        # Assert
        self.assertEqual(result, self.sample_query)

    @pytest.mark.asyncio
    async def test_retrieve_relevant_documents(self):
        """Test that _retrieve_relevant_documents calls vector_retriever_port.search."""
        # Arrange
        query_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]

        # Act
        documents = await self.query_service._retrieve_relevant_documents(query_embedding)

        # Assert
        self.assertEqual(len(documents), 2)
        self.assertEqual(documents[0], self.doc1)
        self.assertEqual(documents[1], self.doc2)
        self.mock_vector_retriever_port.search.assert_called_once_with(query_embedding)

    @pytest.mark.asyncio
    async def test_build_context_messages(self):
        """Test that _build_context_messages creates the expected message list."""
        # Arrange
        user_query = "What is the meaning of life?"
        retrieved_documents = [self.doc1, self.doc2]

        # Act
        messages = await self.query_service._build_context_messages(user_query, retrieved_documents)

        # Assert
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0].role, MessageRole.SYSTEM)
        self.assertEqual(messages[0].content, self.mock_rag_config.system_prompt)
        self.assertEqual(messages[1].role, MessageRole.SYSTEM)
        self.assertIn("Document 1", messages[1].content)
        self.assertIn("Document 2", messages[1].content)
        self.assertEqual(messages[2].role, MessageRole.USER)
        self.assertEqual(messages[2].content, user_query)

    @pytest.mark.asyncio
    async def test_build_context_messages_with_empty_documents(self):
        """Test _build_context_messages with empty document list."""
        # Arrange
        user_query = "What is the meaning of life?"
        retrieved_documents = []

        # Act
        messages = await self.query_service._build_context_messages(user_query, retrieved_documents)

        # Assert
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[1].content, "Here the context\n\n")

    @pytest.mark.asyncio
    async def test_process_query_with_embedding_error(self):
        """Test process_query when embedding_port raises an exception."""
        # Arrange
        self.mock_embedding_port.embed_text.side_effect = Exception("Embedding error")

        # Act & Assert
        with self.assertRaises(Exception) as context:
            await self.query_service.process_query(self.sample_query)
        
        self.assertIn("Embedding error", str(context.exception))

    @pytest.mark.asyncio
    async def test_process_query_with_vector_retriever_error(self):
        """Test process_query when vector_retriever_port raises an exception."""
        # Arrange
        self.mock_vector_retriever_port.search.side_effect = Exception("Vector retrieval error")

        # Act & Assert
        with self.assertRaises(Exception) as context:
            await self.query_service.process_query(self.sample_query)
        
        self.assertIn("Vector retrieval error", str(context.exception))

    @pytest.mark.asyncio
    async def test_process_query_with_llm_error(self):
        """Test process_query when llm_port raises an exception."""
        # Arrange
        self.mock_llm_port.generate_response.side_effect = Exception("LLM error")

        # Act & Assert
        with self.assertRaises(Exception) as context:
            await self.query_service.process_query(self.sample_query)
        
        self.assertIn("LLM error", str(context.exception))

    @pytest.mark.asyncio
    async def test_process_query_data_flow(self):
        """Test the complete data flow through process_query."""
        # Act
        await self.query_service.process_query(self.sample_query)

        # Assert the flow of data through the service
        # 1. Embedding is created
        self.mock_embedding_port.embed_text.assert_called_once_with(self.sample_query.content)

        # 2. Vector search is performed with the embedding
        embedding = self.mock_embedding_port.embed_text.return_value
        self.mock_vector_retriever_port.search.assert_called_once_with(embedding)

        # 3. LLM generates a response
        self.mock_llm_port.generate_response.assert_called_once()

    @patch('logging.getLogger')
    def test_initialization(self, mock_logger):
        """Test QueryService initialization and logging setup."""
        # Arrange
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        # Act
        service = QueryService(
            vector_retriever_port=self.mock_vector_retriever_port,
            llm_port=self.mock_llm_port,
            embedding_port=self.mock_embedding_port,
            rag_config=self.mock_rag_config,
        )

        # Assert
        self.assertEqual(service.vector_retriever_port, self.mock_vector_retriever_port)
        self.assertEqual(service.llm_port, self.mock_llm_port)
        self.assertEqual(service.embedding_port, self.mock_embedding_port)
        self.assertEqual(service.rag_config, self.mock_rag_config)
        mock_logger_instance.info.assert_called_with("QueryService initialized successfully")

    @pytest.mark.asyncio
    async def test_process_query_with_no_documents_retrieved(self):
        """Test process_query when no documents are retrieved."""
        # Arrange
        self.mock_vector_retriever_port.search.return_value = []

        # Act
        result = await self.query_service.process_query(self.sample_query)

        # Assert
        self.assertIsInstance(result, RAGResponse)
        self.assertEqual(len(result.sources), 0)
        self.assertEqual(result.content, "This is a test response from the LLM")

    @pytest.mark.asyncio
    async def test_process_query_with_single_document(self):
        """Test process_query with only one document retrieved."""
        # Arrange
        self.mock_vector_retriever_port.search.return_value = [self.doc1]

        # Act
        result = await self.query_service.process_query(self.sample_query)

        # Assert
        self.assertIsInstance(result, RAGResponse)
        self.assertEqual(len(result.sources), 1)
        self.assertEqual(result.sources[0], self.doc1)

    @pytest.mark.asyncio
    async def test_build_context_messages_content_format(self):
        """Test the specific format of context messages content."""
        # Arrange
        user_query = "Test query"
        retrieved_documents = [self.doc1, self.doc2]

        # Act
        messages = await self.query_service._build_context_messages(user_query, retrieved_documents)

        # Assert
        context_content = messages[1].content
        self.assertIn("Here the context", context_content)
        self.assertIn("Document 1:\nDocument 1 content", context_content)
        self.assertIn("Document 2:\nDocument 2 content", context_content)

    @pytest.mark.asyncio
    async def test_process_query_preserves_llm_response_fields(self):
        """Test that process_query preserves all fields from LLM response."""
        # Arrange
        custom_response = Response(
            content="Custom response content",
            model_used="custom-model",
            processing_time_ms=250,
            input_tokens=150,
            output_tokens=75
        )
        self.mock_llm_port.generate_response.return_value = custom_response

        # Act
        result = await self.query_service.process_query(self.sample_query)

        # Assert
        self.assertEqual(result.content, "Custom response content")
        self.assertEqual(result.model_used, "custom-model")
        self.assertEqual(result.processing_time_ms, 250)
        self.assertEqual(result.input_tokens, 150)
        self.assertEqual(result.output_tokens, 75)
        self.assertEqual(result.sources, [self.doc1, self.doc2])

    @pytest.mark.asyncio
    async def test_validate_query_with_none_content(self):
        """Test _validate_query with None content."""
        # Arrange
        query_with_none = Query(content=None)

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            await self.query_service._validate_query(query_with_none)
        
        self.assertIn("Query content cannot be empty", str(context.exception))

    @pytest.mark.asyncio
    async def test_retrieve_relevant_documents_with_empty_embedding(self):
        """Test _retrieve_relevant_documents with empty embedding."""
        # Arrange
        empty_embedding = []

        # Act
        documents = await self.query_service._retrieve_relevant_documents(empty_embedding)

        # Assert
        self.mock_vector_retriever_port.search.assert_called_once_with(empty_embedding)
        self.assertEqual(documents, [self.doc1, self.doc2])
