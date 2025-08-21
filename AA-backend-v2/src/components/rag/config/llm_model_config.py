from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMModelConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='LLM_', extra="forbid")
    model_name: str
    temperature: float = 0.2
    max_tokens: int = 2048
