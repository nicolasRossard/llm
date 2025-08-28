from abc import ABC, abstractmethod
from typing import List

from src.components.rag.domain.value_objects import DocumentRetrieval
from src.components.rag.domain.value_objects.extracted_content import ExtractedContent


class TextChunkingPort(ABC):
    """
    Port interface for chunking text into smaller segments.
    """

    @abstractmethod
    async def chunk_text(self, extracted_content: ExtractedContent) -> List[DocumentRetrieval]:
        """
        Splits text into chunks with a specified overlap.

        Args:
            extracted_content: An ExtractedContent object containing the text to be chunked

        Returns:
            List[DocumentRetrieval]: A list of DocumentRetrieval objects containing
                the processed text chunks with metadata.
        """
        pass
