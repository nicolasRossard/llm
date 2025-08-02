from abc import ABC, abstractmethod
from domain.schema.question import Question
from domain.schema.answer import Answer


class AnswerQuestion(ABC):
    @abstractmethod
    def execute(self, question: Question) -> Answer:
        pass
