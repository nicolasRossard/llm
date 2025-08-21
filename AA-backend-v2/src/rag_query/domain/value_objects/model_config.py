from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    model_config = {
        "extra": "forbid",  # Disallow extra fields not defined in the model
        "allow_mutation": False,   # Make the model immutable after creation
    }

    temperature: float = Field(default=0.2, ge=0, le=1)
    max_tokens: int = Field(default=2048, description="Maximum number of tokens to generate in the response")
