from enum import Enum


class MessageRole(str, Enum):
    """Role of the message in the conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    