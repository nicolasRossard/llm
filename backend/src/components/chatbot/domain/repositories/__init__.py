"""
Interface for repositories
"""

from .conversation_repository import ConversationRepository
from .knowledge_repository import KnowledgeRepository

__all__ = ["ConversationRepository", "KnowledgeRepository"]
