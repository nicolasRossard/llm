import io
import logging

import PyPDF2

from src.components.chatbot.application.ports.driven.text_extraction_port import TextExtractionPort
from src.components.chatbot.domain.value_objects.input_document import InputDocument, DocumentType


class PyPDFTextExtractionAdapter(TextExtractionPort):
    """Implementation of the TextExtractionPort interface using pypdf2.
    
    This adapter provides concrete implementations for:
    * Extracting text from different document formats (currently only PDF)
    """
    
    def __init__(self):
        """Initialize the document processing adapter.
        """
        self.logger = logging.getLogger(self.__class__.__name__)

    async def extract_text(self, document: InputDocument) -> str:
        """Extract text from a document based on its type.
        
        Args:
            document: The input document to extract text from
            
        Returns:
            str: The extracted text content
            
        Raises:
            ValueError: If document type is not supported
        """
        self.logger.info(f"Extracting text from {document.type.value} document")
        
        if document.type == DocumentType.PDF:
            return await self._extract_text_from_pdf(document.content)
        else:
            error_msg = f"Unsupported document type: {document.type.value}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
    
    async def _extract_text_from_pdf(self, content: bytes) -> tuple[str, dict]:
        """Extract text and global metadata from a PDF document.
        
        Args:
            content: The binary content of the PDF document
            
        Returns:
            tuple: A tuple containing (extracted_text, metadata_dict)
                - extracted_text (str): The extracted text content
                - metadata_dict (dict): Global metadata from the PDF
            
        Raises:
            Exception: If there is an error processing the PDF
        """
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
            
            # Extract global metadata
            metadata = {}
            if pdf_reader.metadata:
                metadata.update(pdf_reader.metadata)
                metadata['pages_count'] = len(pdf_reader.pages)
            
            self.logger.info(f"Successfully extracted {len(text)} characters and metadata from PDF")
            return text, metadata
        except Exception as e:
            error_msg = f"Error extracting text from PDF: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
