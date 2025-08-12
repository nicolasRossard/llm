from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class UserPreferences(BaseModel):
    """User preferences for customizing responses"""
    language: str = "fr"
    response_style: str = "balanced"  # concise, balanced, detailed
    technical_level: str = "intermediate"  # beginner, intermediate, expert
    preferred_topics: List[str] = Field(default_factory=list)
    avoided_topics: List[str] = Field(default_factory=list)


class UserContext(BaseModel):
    """
    UserContext Entity - User context and preferences
    Enables chatbot response personalization
    """
    model_config = ConfigDict(frozen=True)

    user_id: str
    session_id: Optional[UUID] = None
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    conversation_history_summary: str = ""
    current_topic: Optional[str] = None
    context_data: Dict[str, Any] = Field(default_factory=dict)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    total_interactions: int = 0

    def update_context(self, new_data: Dict[str, Any]) -> None:
        """Updates the context with new data"""
        self.context_data.update(new_data)
        self.last_activity = datetime.now(timezone.utc)

    def increment_interactions(self) -> None:
        """Increments the interaction counter"""
        self.total_interactions += 1
        self.last_activity = datetime.now(timezone.utc)

    def update_topic(self, topic: str) -> None:
        """Updates the current conversation topic"""
        self.current_topic = topic
        self.last_activity = datetime.now(timezone.utc)

    def add_to_history_summary(self, summary: str) -> None:
        """Appends to the conversation history summary"""
        if self.conversation_history_summary:
            self.conversation_history_summary += f" | {summary}"
        else:
            self.conversation_history_summary = summary

    def is_new_user(self) -> bool:
        """Checks if this is a new user"""
        return self.total_interactions == 0

    def get_personalization_data(self) -> Dict[str, Any]:
        """Returns personalization data for the LLM"""
        return {
            "language": self.preferences.language,
            "response_style": self.preferences.response_style,
            "technical_level": self.preferences.technical_level,
            "current_topic": self.current_topic,
            "preferred_topics": self.preferences.preferred_topics,
            "is_new_user": self.is_new_user(),
            "total_interactions": self.total_interactions
        }
