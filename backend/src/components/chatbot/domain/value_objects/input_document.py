from typing import BinaryIO, Optional, Dict, Any

from pydantic import BaseModel
from enum import Enum

class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"

class InputDocument(BaseModel):
    """
    Represents an input document with its content and formalized type.

    Attributes:
        content (BinaryIO): The binary content of the document.
        type (DocumentType): The formalized type of the document.
    """
    # TODO add id
    filename: str
    content: bytes
    type: DocumentType

class IngestionStatus(Enum):
    SUCCESS = "success"  # All vectors were inserted
    PARTIAL = "partial"  # Some vectors were inserted, but not all
    ERROR = "error"      # No vectors were inserted


class DocumentIngestionResult(BaseModel):
    """
    Represents the result of inserting document chunks into a vector database.
    
    Attributes:
        total_chunks (int): Total number of chunks created from the document.
        ingested_chunks (int): Number of chunks successfully ingested.
        failed_chunks (int): Number of chunks that failed to ingest.
        status (IngestionStatus): Status of the ingestion operation.
        chunk_ids (Optional[List[str]]): IDs of the successfully stored chunks.
        metrics (Optional[Dict[str, Any]]): Performance metrics for the operation.
    """
    total_chunks: int
    ingested_chunks: int
    failed_chunks: int
    status: IngestionStatus
    metrics: Optional[Dict[str, Any]] = None