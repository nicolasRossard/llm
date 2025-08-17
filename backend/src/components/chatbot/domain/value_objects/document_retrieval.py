from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel


class DocumentRetrieval(BaseModel):
    """Information source used to generate the response"""

    id: UUID = uuid4()
    content: str
    metadata: Optional[dict] = None
    score: Optional[float] = None  # Used for ranking results, e.g. cosine similarity score


class DocumentRetrievalVector(DocumentRetrieval):
    vector: list[float]
