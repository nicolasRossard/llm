from application.ports.server_side.llm_client import LlmClient
from application.ports.server_side.vector_search_port import VectorSearchPort
from domain.schema.document_chunk import DocumentChunk
from domain.schema.query import Question
from domain.schema.answer import Answer


class RagService:
    def __init__(self, vector_port: VectorSearchPort, llm: LlmClient):
        self.vector_port = vector_port
        self.llm = llm

    def process(self, question: Question) -> tuple[Answer, DocumentChunk]:
        context = self.vector_port.search(question.text)
        answer_text = self.llm.generate_answer(question.text, context)
        return Answer(text=answer_text), context
