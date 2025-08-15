from typing import BinaryIO

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

    content: BinaryIO
    type: DocumentType
