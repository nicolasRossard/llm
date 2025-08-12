from abc import ABC, abstractmethod
from domain.schema.query import Query
from domain.schema.answer import Answer


class AnswerQuestion(ABC):
    @abstractmethod
    def execute(self, question: Query) -> Answer:
        pass
