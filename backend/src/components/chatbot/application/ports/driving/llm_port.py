from abc import ABC, abstractmethod


class LlmPort(ABC):
    @abstractmethod
    def generate_answer(self, question: str, context: List[DocumentChunk]) -> str:
        pass