import logging
from io import BytesIO
from annotated_types import doc
from docling.datamodel.base_models import DocumentStream, InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, smolvlm_picture_description
from docling_core.types import DoclingDocument
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

        self.logger.debug(f"extract_text :: Processing document: {document.filename}")

        # if document.type == "application/pdf" or ".pdf":  TODO improve PDF with images handling ?
        #     self.logger.debug("extract_text :: Detected PDF format, applying PDF-specific options")
        #     docling_document: DoclingDocument = await self.pdf_extract_with_image_description(source)
        #
        # else:
        #     self.logger.debug("extract_text :: No PDF format, applying PDF-specific options")
        #     converter = DocumentConverter()
        #     docling_document: DoclingDocument = converter.convert(source).document

        converter = DocumentConverter()
        docling_document: DoclingDocument = converter.convert(source).document
        extracted_text = docling_document.export_to_markdown()
        self.logger.debug(f"extract_text :: Extracted text length: {len(extracted_text)}")
        
        result = ExtractedContent(
            text=extracted_text,
            metadata={
                "filename": document.filename,
                "source_format": "docling",
                "format": "md",
            } # TODO standardize metadata across the application
        )
        
        self.logger.info("extract_text :: Text extraction completed")
        return result

    async def pdf_extract_with_image_description(self, source: DocumentStream) -> DoclingDocument:
        """
        Extract text content from a document and include image descriptions.

        Args:
            source (DocumentStream): The input document stream to extract text from.

        Returns:
            ExtractedContent: The extracted text content with image descriptions and metadata.
        """
        self.logger.info("pdf_extract_with_image_description :: Starting text extraction with image descriptions")

        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_picture_description = True
        pipeline_options.picture_description_options = (
            smolvlm_picture_description  # <-- the model choice
        )
        pipeline_options.picture_description_options.prompt = (
            "Describe the image in three sentences in French. Be concise and accurate."
        )
        pipeline_options.images_scale = 2.0
        pipeline_options.generate_picture_images = True

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options,
                )
            }
        )
        return converter.convert(source).document
