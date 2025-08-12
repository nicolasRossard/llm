from abc import ABC, abstractmethod
from typing import List
from domain.schema.document_chunk import DocumentChunk


class VectorSearchPort(ABC):
    @abstractmethod
    def search(self, query: str) -> List[DocumentChunk]:
        pass