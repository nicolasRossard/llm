from pydantic import BaseModel


class DocumentChunk(BaseModel):
    id: str
    text: str
    score: float
