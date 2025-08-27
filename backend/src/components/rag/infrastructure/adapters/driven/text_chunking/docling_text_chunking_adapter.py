import logging
from io import BytesIO
from typing import List

from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
from docling.datamodel.base_models import DocumentStream

from src.components.rag.application.ports.driven.text_chunking_port import TextChunkingPort
from src.components.rag.domain.value_objects import DocumentRetrieval
from src.components.rag.domain.value_objects.extracted_content import ExtractedContent


class DoclingTextChunkingAdapter(TextChunkingPort):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def _create_document_stream_from_string(content: str, filename: str) -> DocumentStream:
        """
        Creates a DocumentStream from a string content.

        Args:
            content (str): The text content to convert to stream.
            filename (str): The filename for the document.

        Returns:
            DocumentStream: Document stream containing the encoded content.
        """
        # Convert string to bytes and create a BytesIO
        bytes_content = content.encode('utf-8')
        stream = BytesIO(bytes_content)

        return DocumentStream(name=filename, stream=stream)

    async def chunk_text(self, extracted_content: ExtractedContent) -> List[DocumentRetrieval]:
        """
        Chunks text content using Docling's HybridChunker.

        Args:
            extracted_content (ExtractedContent): Content to be chunked with metadata.

        Returns:
            List[DocumentRetrieval]: List of chunked documents with metadata.
        """
        self.logger.info("chunk_text :: Starting text chunking process")
        
        # Convert string to Docling document
        self.logger.debug(f"chunk_text :: Processing content from file: {extracted_content.metadata.get('filename', 'unknown.txt')}")
        converter = DocumentConverter()
        document_stream = self._create_document_stream_from_string(
            content=extracted_content.text,
            filename=extracted_content.metadata.get("filename", "unknown.txt")
        )
        doc = converter.convert(
            source=document_stream,
        ).document

        # Instantiate and apply HybridChunker
        self.logger.info("chunk_text :: Applying HybridChunker to document")
        chunker = HybridChunker()
        chunks = list(chunker.chunk(dl_doc=doc))
        self.logger.debug(f"chunk_text :: Generated {len(chunks)} chunks")

        # Convert chunks to DocumentRetrieval
        document_retrievals: List[DocumentRetrieval] = []

        for i, chunk in enumerate(chunks):
            # Create metadata for this chunk
            chunk_metadata = {
                **extracted_content.metadata,  # Inherit metadata from original document
                "chunk_index": i,
                "chunk_type": type(chunk).__name__,
            }

            # Create DocumentRetrieval
            doc_retrieval = DocumentRetrieval(
                content=chunk.text,
                metadata=chunk_metadata
            )

            document_retrievals.append(doc_retrieval)

        self.logger.info("chunk_text :: Text chunking process completed")
        return document_retrievals
