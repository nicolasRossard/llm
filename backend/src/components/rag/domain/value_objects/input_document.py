from typing import BinaryIO, Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class InputDocument(BaseModel):
    """
    Represents an input document with its content and formalized type.

    Attributes:
        content (bytes): The binary content of the document.
        type (InputDocumentType): The formalized type of the document.
    """
    model_config = ConfigDict(frozen=True)
    
    # TODO add id
    filename: str = Field(..., description="The name of the document file")
    content: bytes = Field(..., description="The binary content of the document")
    type: str = Field(..., description="The formalized type of the document")


class StoreDocumentStatus(Enum):
    SUCCESS = "success"  # All vectors were inserted
    PARTIAL = "partial"  # Some vectors were inserted, but not all
    ERROR = "error"      # No vectors were inserted


class StoreDocumentResult(BaseModel):
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
        >>> result = StoreDocumentResult(
        ...     total_chunks=100,
        ...     ingested_chunks=95,
        ...     failed_chunks=5,
        ...     status=StoreDocumentStatus.PARTIAL,
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
        metrics (Optional[Dict[str, Any]]): Performance metrics for the operation.
    """
    model_config = ConfigDict(frozen=True)
    
    total_chunks: int = Field(..., description="Total number of chunks created from the document")
    ingested_chunks: int = Field(..., description="Number of chunks successfully ingested into the vector database")
    failed_chunks: int = Field(..., description="Number of chunks that failed during the ingestion process")
    status: StoreDocumentStatus = Field(..., description="Overall status of the ingestion operation")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Performance metrics and additional metadata for the operation, such as processing time, memory usage, or error details")