from abc import ABC, abstractmethod


class EmbeddingPort(ABC):
    """Port interface for generating vector embeddings from text."""

    @abstractmethod
    async def generate_embedding(self, text: str) -> list[float]:
        """Generate an embedding vector for a given text.

        Args:
            text: Input text to convert into a vector representation.

        Returns:
            A list of floats representing the embedding vector.
        """
        pass
