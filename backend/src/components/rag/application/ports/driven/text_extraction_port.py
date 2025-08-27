from abc import ABC, abstractmethod

from src.components.rag.domain.value_objects import InputDocument
from src.components.rag.domain.value_objects.extracted_content import ExtractedContent


class TextExtractionPort(ABC):
    """
    Port interface for extracting text from documents.
    """

    @abstractmethod
    def extract_text(self, file: InputDocument) -> ExtractedContent:
        """
        Extracts text from a document and global metadata.

        Args:
            file (InputDocument): An InputDocument object containing the file content and metadata.

        Returns:
            ExtractedContent: Object containing the extracted text and associated metadata.
        """
        pass