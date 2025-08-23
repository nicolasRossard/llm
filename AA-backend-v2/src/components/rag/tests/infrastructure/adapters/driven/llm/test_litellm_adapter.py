import unittest
from unittest.mock import patch, AsyncMock
import pytest

from src.components.rag.infrastructure.adapters.driven.litellm_proxy.litellm_base_adapter import LiteLLMBaseAdapter
from src.components.rag.infrastructure.adapters.driven.litellm_proxy.litellm_config import LiteLLMConfig


class TestLiteLLMBaseAdapter(unittest.TestCase):
    """Test cases for LiteLLMBaseAdapter.

    These tests focus on verifying the behavior of LiteLLMBaseAdapter while mocking
    external HTTP calls to ensure isolated testing.
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a sample configuration for testing
        self.test_config = LiteLLMConfig(
            api_key="test-api-key",
            base_url="http://test-url.com",
            provider="ollama",
            default_chat_model="llama3.2:1b",
            default_embedding_model="nomic-embed-text:v1.5",
            timeout=10.0,
            temperature=0.5,
            max_tokens=1000
        )

        # Sample response for chat completion
        self.chat_completion_response = {
            'id': 'chatcmpl-b9ace196-fbea-41aa-969f-ad71ea55b674',
            'created': 1755961946,
            'model': 'ollama/llama3.2:1b',
            'object': 'chat.completion',
            'system_fingerprint': None,
            'choices': [
                {
                    'finish_reason': 'stop',
                    'index': 0,
                    'message': {
                        'content': "I'm doing well, thank you for asking. How can I assist you today?",
                        'role': 'assistant',
                        'tool_calls': None,
                        'function_call': None
                    }
                }
            ],
            'usage': {
                'completion_tokens': 18,
                'prompt_tokens': 34,
                'total_tokens': 52,
                'completion_tokens_details': None,
                'prompt_tokens_details': None
            }
        }

        # Sample response for embeddings
        self.embeddings_response = {
            'object': 'list',
            'data': [
                {
                    'object': 'embedding',
                    'embedding': [0.1, 0.2, 0.3, 0.4, 0.5],  # Simplified vector
                    'index': 0
                }
            ],
            'model': 'ollama/nomic-embed-text:v1.5',
            'usage': {
                'prompt_tokens': 4,
                'total_tokens': 4
            }
        }

    @patch.object(LiteLLMBaseAdapter, '_make_request')
    @pytest.mark.asyncio
    async def test_chat_completion(self, mock_make_request):
        """Test the chat_completion method with mocked _make_request."""
        # Setup
        mock_make_request.return_value = AsyncMock(return_value=self.chat_completion_response)()
        adapter = LiteLLMBaseAdapter(config=self.test_config)
        messages = [{"role": "user", "content": "Hello, how are you?"}]

        # Execute
        response = await adapter.chat_completion(messages)

        # Assert
        mock_make_request.assert_called_once()
        self.assertEqual(response, self.chat_completion_response)

        # Verify the payload sent to _make_request
        args, kwargs = mock_make_request.call_args
        self.assertEqual(args[0], "chat/completions")
        self.assertEqual(args[1]["model"], "ollama/llama3.2:1b")
        self.assertEqual(args[1]["messages"], messages)
        self.assertEqual(args[1]["temperature"], self.test_config.temperature)
        self.assertEqual(args[1]["max_tokens"], self.test_config.max_tokens)

    @patch.object(LiteLLMBaseAdapter, '_make_request')
    @pytest.mark.asyncio
    async def test_chat_completion_with_custom_params(self, mock_make_request):
        """Test chat_completion with custom parameters."""
        # Setup
        mock_make_request.return_value = AsyncMock(return_value=self.chat_completion_response)()
        adapter = LiteLLMBaseAdapter(config=self.test_config)
        messages = [{"role": "user", "content": "Hello, how are you?"}]

        # Execute with custom parameters
        response = await adapter.chat_completion(
            messages,
            model="custom/model",
            temperature=0.8,
            max_tokens=500,
            stream=True
        )

        # Assert
        mock_make_request.assert_called_once()

        # Verify custom parameters were used
        args, kwargs = mock_make_request.call_args
        self.assertEqual(args[1]["model"], "custom/model")
        self.assertEqual(args[1]["temperature"], 0.8)
        self.assertEqual(args[1]["max_tokens"], 500)
        self.assertEqual(args[1]["stream"], True)

    @patch.object(LiteLLMBaseAdapter, '_make_request')
    @pytest.mark.asyncio
    async def test_embeddings(self, mock_make_request):
        """Test the embeddings method with mocked _make_request."""
        # Setup
        mock_make_request.return_value = AsyncMock(return_value=self.embeddings_response)()
        adapter = LiteLLMBaseAdapter(config=self.test_config)
        input_text = "Hello world"

        # Execute
        response = await adapter.embeddings(input_text)

        # Assert
        mock_make_request.assert_called_once()
        self.assertEqual(response, self.embeddings_response)

        # Verify the payload sent to _make_request
        args, kwargs = mock_make_request.call_args
        self.assertEqual(args[0], "embeddings")
        self.assertEqual(args[1]["model"], "ollama/nomic-embed-text:v1.5")
        self.assertEqual(args[1]["input"], input_text)

    @patch.object(LiteLLMBaseAdapter, '_make_request')
    @pytest.mark.asyncio
    async def test_embeddings_with_custom_model(self, mock_make_request):
        """Test embeddings with custom model parameter."""
        # Setup
        mock_make_request.return_value = AsyncMock(return_value=self.embeddings_response)()
        adapter = LiteLLMBaseAdapter(config=self.test_config)
        input_text = "Hello world"
        custom_model = "custom/embedding-model"

        # Execute
        response = await adapter.embeddings(input_text, model=custom_model)

        # Assert
        mock_make_request.assert_called_once()

        # Verify custom model was used
        args, kwargs = mock_make_request.call_args
        self.assertEqual(args[1]["model"], custom_model)

    def test_get_config_summary(self):
        """Test the get_config_summary method."""
        # Setup
        adapter = LiteLLMBaseAdapter(config=self.test_config)

        # Execute
        summary = adapter.get_config_summary()

        # Assert
        self.assertEqual(summary["base_url"], "http://test-url.com")
        self.assertEqual(summary["provider"], "ollama")
        self.assertEqual(summary["default_chat_model"], "llama3.2:1b")
        self.assertEqual(summary["default_embedding_model"], "nomic-embed-text:v1.5")
        self.assertEqual(summary["timeout"], 10.0)
        self.assertEqual(summary["temperature"], 0.5)
        self.assertEqual(summary["max_tokens"], 1000)
        self.assertEqual(summary["api_key"], "test-api...")  # Should be masked

    def test_initialization(self):
        """Test adapter initialization and configuration."""
        # Execute
        adapter = LiteLLMBaseAdapter(config=self.test_config)

        # Assert
        self.assertEqual(adapter.default_litellm_chat_model, "ollama/llama3.2:1b")
        self.assertEqual(adapter.default_litellm_embedding_model, "ollama/nomic-embed-text:v1.5")
        self.assertEqual(adapter.headers["Authorization"], "Bearer test-api-key")
        self.assertEqual(adapter.headers["Content-Type"], "application/json")

    @patch('httpx.AsyncClient.post')
    @pytest.mark.asyncio
    async def test_make_request_implementation(self, mock_post):
        """Test the actual implementation of _make_request method."""
        # Setup
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_response.json.return_value = self.chat_completion_response
        mock_post.return_value = mock_response

        adapter = LiteLLMBaseAdapter(config=self.test_config)

        # Execute
        response = await adapter._make_request(
            "chat/completions",
            {"model": "test-model", "messages": []}
        )

        # Assert
        mock_post.assert_called_once()
        self.assertEqual(response, self.chat_completion_response)

        # Verify URL formation
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs["url"], "http://test-url.com/chat/completions")
        self.assertEqual(kwargs["headers"], adapter.headers)
        self.assertEqual(kwargs["json"], {"model": "test-model", "messages": []})