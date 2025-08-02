from abc import ABC, abstractmethod
from typing import List
from domain.schema.document_chunk import DocumentChunk


class LlmClient(ABC):
    @abstractmethod
    def generate_answer(self, question: str, context: List[DocumentChunk]) -> str:
        pass