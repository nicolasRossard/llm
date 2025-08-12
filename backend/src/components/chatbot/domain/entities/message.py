from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict


class MessageRole(str, Enum):
    """Role of the message in the conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageStatus(str, Enum):
    """Message processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class Message(BaseModel):
    """
    Message Entity - Represents an individual message in a conversation
    """
    model_config = ConfigDict(frozen=True, use_enum_values=True)

    id: UUID = Field(default_factory=uuid4)
    conversation_id: UUID
    role: MessageRole
    content: str
    status: MessageStatus = MessageStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    processing_time_ms: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Specific to RAG
    retrieved_documents: List[str] = Field(default_factory=list)
    relevance_score: Optional[float] = None

    def is_user_message(self) -> bool:
        """Checks if the message comes from the user"""
        return self.role == MessageRole.USER

    def is_assistant_message(self) -> bool:
        """Checks if the message comes from the assistant"""
        return self.role == MessageRole.ASSISTANT

    def mark_as_processing(self) -> None:
        """Marks the message as being processed"""
        self.status = MessageStatus.PROCESSING

    def mark_as_completed(self, processing_time_ms: int) -> None:
        """Marks the message as successfully processed"""
        self.status = MessageStatus.COMPLETED
        self.processing_time_ms = processing_time_ms

    def mark_as_error(self, error_details: Dict[str, Any]) -> None:
        """Marks the message as having an error"""
        self.status = MessageStatus.ERROR
        self.metadata.update({"error": error_details})

    def add_rag_context(self, documents: List[str], relevance_score: float) -> None:
        """Adds RAG context to the message"""
        self.retrieved_documents = documents
        self.relevance_score = relevance_score

    def get_content_preview(self, max_length: int = 100) -> str:
        """Returns a preview of the message content"""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + "..."
