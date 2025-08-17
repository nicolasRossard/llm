"""Ollama Embedding Adapter implementing the EmbeddingPort interface."""

import logging
import httpx

from src.components.chatbot.application.ports.driven import EmbeddingPort


logger = logging.getLogger(__name__)


class OllamaEmbeddingAdapter(EmbeddingPort):
    """Adapter for the Ollama embedding API implementing the EmbeddingPort.
    
    This is a driven adapter that translates between the application's
    domain model and the external Ollama embedding API.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "nomic-embed-text:v1.5",
        fallback_dimension: int = 768,
    ) -> None:
        """Initialize the adapter with API connection details.
        
        Args:
            base_url: Ollama API base URL.
            model: Model identifier to use for embeddings.
            fallback_dimension: Dimension of fallback embeddings if API fails.
        """
        super().__init__(model=model, fallback_dimension=fallback_dimension)
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(
            "Initialized OllamaEmbeddingAdapter with model '%s' at '%s'",
            self.model,
            self.base_url,
        )
        
    async def generate_embedding(self, text: str) -> list[float]:
        """Generate an embedding vector for a given text.
        
        Args:
            text: Input text to convert into a vector representation.
            
        Returns:
            A list of floats representing the embedding vector.
        """
        # Handle empty input
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding generation")
            return self._get_fallback_embedding()
            
        try:
            # Prepare request payload - Ollama uses the /api/embeddings endpoint for embeddings
            payload = {
                "model": self.model,
                "prompt": text
            }
            
            # Call Ollama API to generate embeddings
            url = f"{self.base_url}/api/embeddings"
            logger.debug(f"Sending embedding request to Ollama API: {url}")
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # Extract embeddings from response
            embedding = result.get("embedding", [])
            if not embedding:
                logger.warning("No embedding returned from Ollama API")
                return self._get_fallback_embedding()
                
            logger.debug(f"Generated embedding with {len(embedding)} dimensions")
            return embedding
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling Ollama API: {e.response.status_code} {e.response.text}")
            return self._get_fallback_embedding()
        except httpx.RequestError as e:
            logger.error(f"Request error calling Ollama API: {str(e)}")
            return self._get_fallback_embedding()
        except Exception as e:
            logger.exception(f"Unexpected error calling Ollama API: {str(e)}")
            return self._get_fallback_embedding()
    
    def _get_fallback_embedding(self) -> list[float]:
        """Generate a fallback embedding when the API call fails.
        
        Returns:
            A list of zeros as a fallback embedding vector
        """
        # In a production environment, you might want a more sophisticated fallback
        # For now, we return a vector of zeros with the correct dimension
        return [0.0] * self.fallback_dimension
