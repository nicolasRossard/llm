from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any


class ExtractedContent(BaseModel):
    """
    Value Object representing extracted content from a document with its metadata.
    Immutable object containing the text content and associated metadata.
    """
    model_config = ConfigDict(frozen=True)

    text: str = Field(..., description="The extracted text content from the document.")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dictionary containing document metadata such as format, creation date, author, etc."
    )
