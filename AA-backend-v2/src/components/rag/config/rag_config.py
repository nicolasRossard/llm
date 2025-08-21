from pydantic_settings import BaseSettings, SettingsConfigDict


class RAGConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='RAG_', extra="forbid")
    system_prompt: str