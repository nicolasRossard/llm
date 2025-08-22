from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict

from .document_retrieval import DocumentRetrieval


class Response(BaseModel):
    """
    Value Object for a llm response.
    Immutable object containing the response and its metadata.
    """
    model_config = ConfigDict(frozen=False)

    content: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_used: Optional[str] = None
    processing_time_ms: Optional[int] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    provider: Optional[str] = None


class RAGResponse(Response):
    """
    Value Object for a llm response using RAG.
    """
    model_config = ConfigDict(frozen=False)
    sources: List[DocumentRetrieval] = Field(None, description="List of document retrievals used to generate the response")

