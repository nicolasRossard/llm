from typing import BinaryIO, Optional, Dict, Any

from pydantic import BaseModel
from enum import Enum


class InputDocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


class InputDocument(BaseModel):
    """
    Represents an input document with its content and formalized type.

    Attributes:
        content (bytes): The binary content of the document.
        type (InputDocumentType): The formalized type of the document.
    """
    # TODO add id
    filename: str
    content: bytes
    type: InputDocumentType


class InputDocumentStatus(Enum):
    SUCCESS = "success"  # All vectors were inserted
    PARTIAL = "partial"  # Some vectors were inserted, but not all
    ERROR = "error"      # No vectors were inserted


class InputDocumentResult(BaseModel):
    """Represents the result of inserting document chunks into a vector database.
    This class encapsulates the outcome of a document ingestion process, providing
    detailed information about the success and failure rates of chunk processing.
        ingested_chunks (int): Number of chunks successfully ingested into the vector database.
        failed_chunks (int): Number of chunks that failed during the ingestion process.
        status (InputDocumentStatus): Overall status of the ingestion operation.
        metrics (Optional[Dict[str, Any]]): Performance metrics and additional metadata
            for the operation, such as processing time, memory usage, or error details.
    Example:
    ```python
        >>> result = InputDocumentResult(
        ...     total_chunks=100,
        ...     ingested_chunks=95,
        ...     failed_chunks=5,
        ...     status=InputDocumentStatus.PARTIAL,
        ...     metrics={"processing_time": 12.5, "memory_used": "256MB"}
        ... )
        >>> print(f"Success rate: {result.ingested_chunks / result.total_chunks * 100:.1f}%")
        Success rate: 95.0%
    ```
    Represents the result of inserting document chunks into a vector database.
    
    Attributes:
        total_chunks (int): Total number of chunks created from the document.
        ingested_chunks (int): Number of chunks successfully ingested.
        failed_chunks (int): Number of chunks that failed to ingest.
        status (InputDocumentStatus): Status of the ingestion operation.
        chunk_ids (Optional[List[str]]): IDs of the successfully stored chunks.
        metrics (Optional[Dict[str, Any]]): Performance metrics for the operation.
    """
    total_chunks: int
    ingested_chunks: int
    failed_chunks: int
    status: InputDocumentStatus
    metrics: Optional[Dict[str, Any]] = None