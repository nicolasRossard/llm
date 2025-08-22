from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMModelConfig(BaseSettings):
    """Configuration settings for Large Language Model.
    
    This class defines the configuration parameters for LLM models including
    model identification, generation parameters, and token limits.
    
    Attributes:
        model_name: The name/identifier of the LLM model to use.
        temperature: Controls randomness in model output (0.0-1.0).
        max_tokens: Maximum number of tokens the model can generate.
    """
    
    model_config = SettingsConfigDict(env_prefix='LLM_', extra="forbid")
    
    model_name: str = Field(description="The name or identifier of the LLM model to use")
    temperature: float = Field(
        default=0.2, 
        description="Controls the randomness of the model output, between 0.0 (deterministic) and 1.0 (random)"
    )
    max_tokens: int = Field(
        default=2048, 
        description="Maximum number of tokens that the model can generate in a single response"
    )
