
from typing import Any, Optional
from pydantic import BaseModel


class LLMConfig(BaseModel):
    model_name: str
    provider: str = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 1000
