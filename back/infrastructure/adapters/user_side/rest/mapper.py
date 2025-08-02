# infrastructure/adapters/input/rest/mapper.py
from domain.schema.question import Question
from domain.schema.answer import Answer
from infrastructure.adapters.user_side.rest.dto import QuestionDTO, AnswerDTO


def to_domain(dto: QuestionDTO) -> Question:
    return Question(text=dto.question)


def to_dto(answer: Answer) -> AnswerDTO:
    return AnswerDTO(answer=answer.text)
