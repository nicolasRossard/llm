import logging
from io import BytesIO
from annotated_types import doc
from docling.datamodel.base_models import DocumentStream
from docling.document_converter import DocumentConverter

from src.components.rag.application.ports.driven.text_extraction_port import TextExtractionPort
from src.components.rag.domain.value_objects import InputDocument
from src.components.rag.domain.value_objects.extracted_content import ExtractedContent


class DoclingTextExtractionAdapter(TextExtractionPort):
    """
    Adapter for text extraction using Docling library.
    
    Implements TextExtractionPort to extract text content from documents
    using the Docling document converter.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    async def extract_text(self, document: InputDocument) -> ExtractedContent:
        """
        Extract text content from a document using Docling converter.

        Args:
            document (InputDocument): The input document to extract text from.

        Returns:
            ExtractedContent: The extracted text content with metadata.
        """
        self.logger.info("extract_text :: Starting text extraction")
        
        buf = BytesIO(document.content)
        source = DocumentStream(name=document.filename, stream=buf)
        converter = DocumentConverter()
        
        self.logger.debug(f"extract_text :: Processing document: {document.filename}")
        doc = converter.convert(source).document

        extracted_text = doc.export_to_markdown()
        self.logger.debug(f"extract_text :: Extracted text length: {len(extracted_text)}")
        
        result = ExtractedContent(
            text=extracted_text,
            metadata={
                "filename": document.filename,
                "source_format": "docling"
            }
        )
        
        self.logger.info("extract_text :: Text extraction completed")
        return result
