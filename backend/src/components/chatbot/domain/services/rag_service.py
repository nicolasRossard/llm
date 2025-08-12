from typing import List, Dict, Any, Tuple
from abc import ABC, abstractmethod

from ..value_objects.query import Query
from ..value_objects.response import Response
from ..entities.message import Message
from ..entities.user_context import UserContext
from ..repositories.knowledge_repository import KnowledgeRepository


class RAGService:
    """
    Domain service for RAG (Retrieval-Augmented Generation) logic.
    Contains the complex business logic for retrieval and generation.
    """

    def __init__(self, knowledge_repository: KnowledgeRepository):
        self._knowledge_repository = knowledge_repository

    def process_query_with_context(
            self,
            query: Query,
            conversation_history: List[Message],
            user_context: UserContext
    ) -> Tuple[List[str], Dict[str, Any]]:
        """
        Processes a query using the conversation context.
        Returns relevant documents and metadata.
        """
        # Enrich the query with context
        enriched_query = self._enrich_query_with_context(query, conversation_history, user_context)

        # Retrieve relevant documents
        relevant_documents = self._knowledge_repository.find_relevant_documents(
            enriched_query.content,
            limit=5,
            filters=self._build_search_filters(user_context)
        )

        # Calculate relevance scores
        relevance_metadata = self._calculate_relevance_scores(
            enriched_query,
            relevant_documents
        )

        return relevant_documents, relevance_metadata

    def _enrich_query_with_context(
            self,
            query: Query,
            history: List[Message],
            context: UserContext
    ) -> Query:
        """Enriches the query with conversation context."""

        # Extract recent conversation context
        recent_context = self._extract_conversation_context(history)

        # Build enriched query content
        enriched_content = query.content

        if recent_context:
            enriched_content = f"Context: {recent_context}\nQuestion: {query.content}"

        if context.current_topic:
            enriched_content = f"Topic: {context.current_topic}\n{enriched_content}"

        return Query(
            content=enriched_content,
            intent=query.intent,
            entities=query.entities,
            metadata={
                **query.metadata,
                "enriched": True,
                "context_length": len(recent_context) if recent_context else 0
            }
        )

    def _extract_conversation_context(self, messages: List[Message]) -> str:
        """Extracts relevant context from recent messages."""
        if not messages:
            return ""

        # Take the last 3 exchanges (max 6 messages)
        recent_messages = messages[-6:]
        context_parts = []

        for message in recent_messages:
            if message.is_user_message():
                context_parts.append(f"User: {message.content}")
            elif message.is_assistant_message():
                # Only take a summary of the assistant's response
                preview = message.get_content_preview(150)
                context_parts.append(f"Assistant: {preview}")

        return " | ".join(context_parts[-4:])  # Limit to max 4 elements

    def _build_search_filters(self, user_context: UserContext) -> Dict[str, Any]:
        """Builds search filters based on the user context."""
        filters = {}

        # Filter by language
        if user_context.preferences.language:
            filters["language"] = user_context.preferences.language

        # Filter by technical level
        if user_context.preferences.technical_level:
            filters["technical_level"] = user_context.preferences.technical_level

        # Filter by preferred topics
        if user_context.preferences.preferred_topics:
            filters["topics"] = user_context.preferences.preferred_topics

        return filters

    def _calculate_relevance_scores(
            self,
            query: Query,
            documents: List[str]
    ) -> Dict[str, Any]:
        """Calculates the relevance scores of retrieved documents."""

        # Basic business logic for relevance calculation
        scores = []
        for doc in documents:
            # Simple relevance calculation (can be improved with advanced metrics)
            common_words = set(query.content.lower().split()) & set(doc.lower().split())
            score = len(common_words) / len(set(query.content.lower().split()))
            scores.append(score)

        return {
            "relevance_scores": scores,
            "average_relevance": sum(scores) / len(scores) if scores else 0,
            "total_documents": len(documents),
            "query_complexity": len(query.content.split())
        }
