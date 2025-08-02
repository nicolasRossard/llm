from pydantic import BaseModel


class Answer(BaseModel):
    text: str
