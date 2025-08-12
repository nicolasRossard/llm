from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict

from .message import Message
from .user_context import UserContext


class Conversation(BaseModel):
    """
    Conversation Entity - Root aggregate for a chat session
    Manages the message history and the conversation context
    """
    model_config = ConfigDict(frozen=True, use_enum_values=True)

    id: UUID = Field(default_factory=uuid4)
    user_id: str
    title: Optional[str] = None
    messages: List[Message] = Field(default_factory=list)
    context: UserContext
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_message(self, message: Message) -> None:
        """Adds a message to the conversation"""
        self.messages.append(message)
        self.updated_at = datetime.now(timezone.utc)

        # Automatically update the title if this is the first user message
        if not self.title and message.is_user_message():
            self.title = self._generate_title_from_message(message.content)

    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        """Retrieves recent messages for context"""
        return self.messages[-limit:] if len(self.messages) > limit else self.messages

    def get_conversation_summary(self) -> str:
        """Generates a conversation summary for context"""
        if not self.messages:
            return "New conversation"

        user_messages = [m for m in self.messages if m.is_user_message()]
        if user_messages:
            return f"Conversation started by: {user_messages[0].content[:100]}..."
        return "Ongoing conversation"

    def update_context(self, new_context_data: Dict[str, Any]) -> None:
        """Updates the user context"""
        self.context.update_context(new_context_data)
        self.updated_at = datetime.now(timezone.utc)

    def is_expired(self, max_idle_hours: int = 24) -> bool:
        """Checks if the conversation is expired"""
        idle_time = datetime.now(timezone.utc) - self.updated_at
        return idle_time.total_seconds() > (max_idle_hours * 3600)

    def deactivate(self) -> None:
        """Deactivates the conversation"""
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)

    def _generate_title_from_message(self, content: str) -> str:
        """Generates a title based on the first message"""
        # Limit to 50 characters and clean up
        clean_content = content.strip().replace('\n', ' ')
        return clean_content[:50] + ('...' if len(clean_content) > 50 else '')
