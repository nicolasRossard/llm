from pydantic import BaseModel, ConfigDict, Field

from .message_role import MessageRole


class Message(BaseModel):
    """
    Message Entity - Represents an individual message in a conversation
    """
    model_config = ConfigDict(frozen=True, use_enum_values=True)

    role: MessageRole = Field(..., description="The role of the message sender")
    content: str = Field(..., description="The text content of the message")
