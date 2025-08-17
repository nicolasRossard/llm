from pydantic import BaseModel

from domain.schema.document_chunk import DocumentChunk


class Answer(BaseModel):
    text: str
    sources: list[DocumentChunk]
