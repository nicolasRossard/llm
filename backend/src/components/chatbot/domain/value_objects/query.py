from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class Query(BaseModel):
    """
    Value Object for a user query.
    Immutable object representing a question/request.
    """
    model_config = ConfigDict(frozen=True)

    content: str
    intent: Optional[str] = None
    entities: List[str] = Field(default_factory=list)
    confidence_score: Optional[float] = None
    language: str = "fr"
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def is_question(self) -> bool:
        """Checks if the query is a question"""
        return "?" in self.content

    def is_complex_query(self) -> bool:
        """Determines if the query is complex (multiple sentences, etc.)"""
        sentences = self.content.split('.')
        return len(sentences) > 2 or len(self.content.split()) > 20

    def get_word_count(self) -> int:
        """Returns the number of words in the query"""
        return len(self.content.split())

    def extract_keywords(self, min_length: int = 3) -> List[str]:
        """Extracts basic keywords from the query"""
        # Simple extraction logic (to be improved with NLP)
        words = self.content.lower().split()
        # Filter out basic stop words
        stop_words = {"le", "la", "les", "de", "du", "des", "et", "ou", "à", "un", "une", "ce", "cette", "ces"}
        keywords = [
            word.strip('.,!?;:')
            for word in words
            if len(word) >= min_length and word.lower() not in stop_words
        ]
        return list(set(keywords))  # Remove duplicates
