from io import BytesIO
from annotated_types import doc
from docling.datamodel.base_models import DocumentStream
from docling.document_converter import DocumentConverter

from src.components.rag.application.ports.driven.text_extraction_port import TextExtractionPort
from src.components.rag.domain.value_objects import InputDocument
from src.components.rag.domain.value_objects.extracted_content import ExtractedContent


class DoclingTextExtractionAdapter(TextExtractionPort):
    async def extract_text(self, document: InputDocument) -> ExtractedContent:
        buf = BytesIO(document.content)
        source = DocumentStream(name=document.filename, stream=buf)
        converter = DocumentConverter()
        doc = converter.convert(source).document

        print(doc.export_to_markdown())
        
        return ExtractedContent(
            text=doc.export_to_markdown(),
            metadata={
                "filename": document.filename,
                "source_format": "docling"
            }
        )
