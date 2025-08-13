from abc import ABC, abstractmethod
from typing import Dict, Any, BinaryIO, List

from src.components.chatbot.domain.value_objects import DocumentRetrieval


class DocumentProcessingPort(ABC):
    """
    Unified interface for all technical operations related to documents.
    """

    @abstractmethod
    def extract_text(self, file_content: BinaryIO, file_type: str) -> str:
        """
        Extracts text from a document based on its type.

        Args:
            file_content (BinaryIO): A binary stream of the file content.
            file_type (str): The type or format of the document
                (e.g., 'pdf', 'docx', 'txt').

        Returns:
            str: The extracted text from the document.
        """
        pass

    @abstractmethod
    def chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[DocumentRetrieval]:
        """
        Splits text into chunks with a specified overlap.

        Args:
            text (str): The text to split.
            chunk_size (int): The maximum number of characters per chunk.
            overlap (int): The number of characters to overlap between
                consecutive chunks.

        Returns:
            List[str]: A list of text chunks.
        """
        pass
