from abc import ABC, abstractmethod


class EmbeddingPort(ABC):
    """Port interface for generating vector embeddings from text."""
    model: str
    fallback_dimension: int

    def __init__(self, model: str, fallback_dimension: int) -> None:
        """Initialize the embedding port with configuration.

        Args:
            model: The embedding model identifier used to generate vectors.
            fallback_dimension: Default embedding dimension if the model does not specify.
        """
        self.model = model
        self.fallback_dimension = fallback_dimension

    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        """Generate an embedding vector for a given text.

        Args:
            text: Input text to convert into a vector representation.

        Returns:
            A list of floats representing the embedding vector.
        """
        pass
