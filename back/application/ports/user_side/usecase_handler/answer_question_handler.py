from application.ports.user_side.usecase.answer_question import AnswerQuestion
from domain.schema.query import Question
from domain.schema.answer import Answer
from domain.service.rag_service import RagService


class AnswerQuestionHandler(AnswerQuestion):
    def __init__(self, rag_service: RagService):
        self.rag_service = rag_service

    def execute(self, question: Question) -> Answer:
        return self.rag_service.process(question)
