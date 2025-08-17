from pydantic import BaseModel, ConfigDict

from .message_role import MessageRole


class Message(BaseModel):
    """
    Message Entity - Represents an individual message in a conversation
    """
    model_config = ConfigDict(frozen=True, use_enum_values=True)

    role: MessageRole
    content: str


