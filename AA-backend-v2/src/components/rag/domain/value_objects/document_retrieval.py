from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DocumentRetrieval(BaseModel):
    """Information source used to generate the response.
    
    Attributes:
        id: Unique identifier for the document retrieval.
        content: The text content of the retrieved document.
        metadata: Optional metadata associated with the document.
        score: Optional ranking score (e.g., cosine similarity score).
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the document retrieval")
    content: str = Field(description="The text content of the retrieved document")
    metadata: Optional[dict] = Field(None, description="Optional metadata associated with the document")
    score: Optional[float] = Field(None, description="Optional ranking score (e.g., cosine similarity score)")


class DocumentRetrievalVector(DocumentRetrieval):
    """Document retrieval with associated vector embedding.
    
    Attributes:
        vector: The vector embedding of the document content.
    """
    
    vector: list[float] = Field(description="The vector embedding of the document content")
