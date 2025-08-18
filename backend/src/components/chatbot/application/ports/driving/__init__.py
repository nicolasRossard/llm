"""
Inputs
All abstract interactions User to the Domain
"""

from .chatbot_port import ChatbotPort
from .document_ingestion_port import DocumentIngestionPort

__all__ = ["ChatbotPort", "DocumentIngestionPort"]
