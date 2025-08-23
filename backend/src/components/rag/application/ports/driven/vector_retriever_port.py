from abc import ABC, abstractmethod
from typing import List

from src.components.rag.domain.value_objects import Query, DocumentRetrieval


class VectorRetrieverPort(ABC):
    """The port follows the hexagonal architecture pattern, allowing different vector database
    implementations to be plugged in without affecting the business logic.

    Examples:
        Implementing a concrete vector store:

        >>> class QdrantVectorStore(VectorRetrieverPort):
                def __init(self, config: RAgConfig):
                    self.config = config
                    ...
        ...     def search(self, query: Query) -> List[DocumentRetrieval]:
        ...         # Implementation specific to Qdrant
        ...         pass

    """

    @abstractmethod
    async def search(self, query: list[float], *args, **kwargs) -> List[DocumentRetrieval]:
        """Search for the most relevant documents given a query.

        Args:
            query (list[float]): The domain vector query object representing the search request.

        Returns:
            List[DocumentRetrieval]: List of retrieved documents ranked by relevance.
        """
        pass
