from abc import ABC, abstractmethod
from src.components.chatbot.domain.value_objects import InputDocument

class TextExtractionPort(ABC):
    """
    Port interface for extracting text from documents.
    """

    @abstractmethod
    def extract_text(self, file: InputDocument) -> tuple[str, dict]:
        """
        Extracts text from a document and global metadata.

        Args:
            file (InputDocument): An InputDocument object containing the file content and metadata.

        Returns:
            tuple[str, dict]: A tuple containing the extracted text and metadata.
        """
        pass