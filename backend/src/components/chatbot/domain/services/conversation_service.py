from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta

from ..entities.conversation import Conversation
from ..entities.message import Message, MessageRole, MessageStatus
from ..entities.user_context import UserContext


class ConversationService:
    """
    Domain service for conversation business logic.
    Manages complex business rules related to conversations.
    """

    def create_new_conversation(self, user_id: str, user_context: UserContext) -> Conversation:
        """Creates a new conversation with the user context."""

        conversation = Conversation(
            user_id=user_id,
            context=user_context
        )

        # Add a system message if needed
        if user_context.is_new_user():
            welcome_message = self._create_welcome_message(conversation.id, user_context)
            conversation.add_message(welcome_message)

        return conversation

    def should_create_new_conversation(
            self,
            current_conversation: Optional[Conversation],
            max_messages: int = 50,
            max_idle_hours: int = 24
    ) -> bool:
        """
        Determines whether to create a new conversation.
        Business rules for conversation segmentation.
        """

        if not current_conversation:
            return True

        # Conversation inactive
        if not current_conversation.is_active:
            return True

        # Too many messages in the current conversation
        if len(current_conversation.messages) >= max_messages:
            return True

        # Conversation expired (due to inactivity)
        if current_conversation.is_expired(max_idle_hours):
            return True

        return False

    def prepare_conversation_for_llm(
            self,
            conversation: Conversation,
            include_system_messages: bool = True
    ) -> List[Dict[str, str]]:
        """
        Prepares the conversation for sending to the LLM.
        Formats according to the language model's expectations.
        """

        messages_for_llm = []

        # Add the system context if requested
        if include_system_messages:
            system_message = self._build_system_message(conversation.context)
            messages_for_llm.append({
                "role": "system",
                "content": system_message
            })

        # Add conversation messages
        for message in conversation.get_recent_messages(limit=10):
            if message.role != MessageRole.SYSTEM:  # Avoid duplicating system messages
                messages_for_llm.append({
                    "role": message.role.value,
                    "content": message.content
                })

        return messages_for_llm

    def analyze_conversation_sentiment(self, conversation: Conversation) -> Dict[str, Any]:
        """
        Analyzes sentiment and conversation patterns.
        Business logic for behavioral analysis.
        """

        user_messages = [m for m in conversation.messages if m.is_user_message()]

        if not user_messages:
            return {"sentiment": "neutral", "engagement": "low"}

        # Basic calculations (to be enhanced with more advanced models)
        total_user_words = sum(len(m.content.split()) for m in user_messages)
        avg_message_length = total_user_words / len(user_messages)

        # Simple pattern detection
        question_count = sum(1 for m in user_messages if "?" in m.content)
        exclamation_count = sum(1 for m in user_messages if "!" in m.content)

        engagement_level = "high" if avg_message_length > 20 else "medium" if avg_message_length > 10 else "low"

        return {
            "sentiment": "positive" if exclamation_count > question_count else "inquisitive" if question_count > 0 else "neutral",
            "engagement": engagement_level,
            "avg_message_length": avg_message_length,
            "question_ratio": question_count / len(user_messages),
            "total_interactions": len(user_messages)
        }

    def _create_welcome_message(self, conversation_id, user_context: UserContext) -> Message:
        """Creates a personalized welcome message."""

        welcome_content = "Bonjour ! Je suis votre assistant IA. Comment puis-je vous aider aujourd'hui ?"

        # Personalize according to preferences
        if user_context.preferences.language != "fr":
            if user_context.preferences.language == "en":
                welcome_content = "Hello! I'm your AI assistant. How can I help you today?"

        return Message(
            conversation_id=conversation_id,
            role=MessageRole.SYSTEM,
            content=welcome_content,
            status=MessageStatus.COMPLETED
        )

    def _build_system_message(self, user_context: UserContext) -> str:
        """Builds the system message for the LLM."""

        personalization = user_context.get_personalization_data()

        system_prompt = f"""You are a helpful and precise AI assistant. 

User information:
- Language: {personalization['language']}
- Response style: {personalization['response_style']}
- Technical level: {personalization['technical_level']}"""

        if personalization['current_topic']:
            system_prompt += f"\n- Current topic: {personalization['current_topic']}"

        if personalization['preferred_topics']:
            system_prompt += f"\n- Interests: {', '.join(personalization['preferred_topics'])}"

        if personalization['is_new_user']:
            system_prompt += "\n\nNote: This is a new user, be particularly welcoming."

        return system_prompt
