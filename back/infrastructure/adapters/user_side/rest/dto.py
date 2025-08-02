from pydantic import BaseModel


class QuestionDTO(BaseModel):
    question: str


class AnswerDTO(BaseModel):
    answer: str

