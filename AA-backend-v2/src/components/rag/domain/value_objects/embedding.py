from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class Embedding(BaseModel):
    """A value object representing an embedding response from a language model.

    This immutable object encapsulates the embedding data along with metadata
    about the generation process, including model information and token usage.

    Attributes:
        model (str): Name or identifier of the model that generated the embeddings.
        embedding (List[float]): The actual embedding vector.
        prompt_tokens (int): Number of prompt tokens used.
        generated_at (datetime): UTC timestamp when the embedding was generated.
        provider (Optional[str]): The embedding provider used to generate the response.
    """
    model_config = ConfigDict(frozen=True)

    model: str = Field(..., description="Name or identifier of the model that generated the embeddings")
    embedding: List[float] = Field(..., description="The actual embedding vector representation")
    prompt_tokens: Optional[int] = Field(default=None, description="Number of prompt tokens used during generation")
    completion_tokens: Optional[int] = Field(default=None, description="Number of completion tokens used during generation")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC timestamp when the embedding was generated")
    provider: Optional[str] = Field(default=None, description="The embedding provider used to generate the response")
    processing_time_ms: Optional[int] = Field(default=None)
