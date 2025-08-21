from pydantic import BaseModel, Field, ConfigDict


class ModelConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    temperature: float = Field(default=0.2, ge=0, le=1)
    max_tokens: int = Field(default=2048, description="Maximum number of tokens to generate in the response")
