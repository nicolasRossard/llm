from abc import ABC, abstractmethod
from typing import Dict, Any, BinaryIO, List

from src.components.chatbot.domain.value_objects import DocumentRetrieval, InputDocument


class DocumentProcessingPort(ABC):
    """
    Unified interface for all technical operations related to documents.
    """

    @abstractmethod
    @abstractmethod
    def extract_text(self, file: InputDocument) -> str:
        """
        Extracts text from a document.

        Args:
            file (InputDocument): An InputDocument object containing the file content and metadata.

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

    @abstractmethod
    def process_document(self, file: InputDocument) -> List[DocumentRetrieval]:
        """
        Processes a document by extracting text and splitting it into chunks.

        Args:
            file (BinaryIO): A binary stream of the file content.
            file_type (str): The type or format of the document
                (e.g., 'pdf', 'docx', 'txt').
        Returns:
            List[DocumentRetrieval]: A list of DocumentRetrieval objects containing
                the processed chunks.
        """
        pass