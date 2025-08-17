from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class Query(BaseModel):
    """
    Value Object for a user query.
    Immutable object representing a question/request.
    """
    model_config = ConfigDict(frozen=True)
    content: str
