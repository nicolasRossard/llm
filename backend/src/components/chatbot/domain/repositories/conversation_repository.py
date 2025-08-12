from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.conversation import Conversation


class ConversationRepository(ABC):
    """
    Repository interface for conversations.
    Defines persistence operations for conversations.
    """

    @abstractmethod
    async def save(self, conversation: Conversation) -> Conversation:
        """Saves a conversation"""
        pass

    @abstractmethod
    async def find_by_id(self, conversation_id: UUID) -> Optional[Conversation]:
        """Finds a conversation by its ID"""
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: str, limit: int = 10) -> List[Conversation]:
        """Finds conversations for a given user"""
        pass

    @abstractmethod
    async def find_active_by_user_id(self, user_id: str) -> Optional[Conversation]:
        """Finds the active conversation for a given user"""
        pass

    @abstractmethod
    async def update(self, conversation: Conversation) -> Conversation:
        """Updates an existing conversation"""
        pass

    @abstractmethod
    async def delete(self, conversation_id: UUID) -> bool:
        """Deletes a conversation"""
        pass

    @abstractmethod
    async def find_expired_conversations(self, hours: int = 24) -> List[Conversation]:
        """Finds expired conversations for cleanup"""
        pass
