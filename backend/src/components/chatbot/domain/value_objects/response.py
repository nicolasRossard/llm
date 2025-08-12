from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ResponseSource(BaseModel):
    """Information source used to generate the response"""
    document_id: str
    title: Optional[str] = None
    relevance_score: float
    excerpt: Optional[str] = None


class Response(BaseModel):
    """
    Value Object for a chatbot response.
    Immutable object containing the response and its metadata.
    """
    model_config = ConfigDict(frozen=True)

    content: str
    confidence_score: float
    sources: List[ResponseSource] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    model_used: Optional[str] = None
    processing_time_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def has_high_confidence(self, threshold: float = 0.8) -> bool:
        """Checks if the response has a high confidence level"""
        return self.confidence_score >= threshold

    def has_sources(self) -> bool:
        """Checks if the response has documented sources"""
        return len(self.sources) > 0

    def get_primary_source(self) -> Optional[ResponseSource]:
        """Returns the primary source (highest relevance score)"""
        if not self.sources:
            return None
        return max(self.sources, key=lambda s: s.relevance_score)

    def get_response_quality_score(self) -> float:
        """Calculates an overall quality score for the response"""
        base_score = self.confidence_score

        # Bonus for sources
        if self.sources:
            source_bonus = min(0.2, len(self.sources) * 0.05)  # Max 0.2
            avg_relevance = sum(s.relevance_score for s in self.sources) / len(self.sources)
            base_score += source_bonus * avg_relevance

        # Bonus for content (reasonable length)
        content_length = len(self.content.split())
        if 10 <= content_length <= 200:  # Optimal length
            base_score += 0.1

        return min(1.0, base_score)  # Cap at 1.0

    def format_for_display(self) -> Dict[str, Any]:
        """Formats the response for user display"""
        return {
            "response": self.content,
            "confidence": self.confidence_score,
            "sources": [
                {
                    "title": source.title or "Document",
                    "relevance": source.relevance_score,
                    "excerpt": source.excerpt
                }
                for source in self.sources
            ] if self.sources else [],
            "quality_score": self.get_response_quality_score(),
            "generated_at": self.generated_at.isoformat()
        }
