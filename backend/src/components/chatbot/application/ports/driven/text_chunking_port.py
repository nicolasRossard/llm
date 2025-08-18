from abc import ABC, abstractmethod
from typing import List
from src.components.chatbot.domain.value_objects import DocumentRetrieval


class TextChunkingPort(ABC):
    """
    Port interface for chunking text into smaller segments.
    """

    @abstractmethod
    def chunk_text(self, text: str, metadata: dict) -> List[DocumentRetrieval]:
        """
        Splits text into chunks with a specified overlap.

        Args:
            text (str): The text to split.
            metadata (dict): Metadata to include with each chunk.

        Returns:
            List[DocumentRetrieval]: A list of DocumentRetrieval objects containing
                the processed text chunks with metadata.
        """
        pass