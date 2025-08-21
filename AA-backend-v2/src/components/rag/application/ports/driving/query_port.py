from abc import ABC, abstractmethod


from src.components.rag.domain.value_objects import Query, Response


class QueryPort(ABC):
    """Abstract interface defining the port for rag query interactions.

    This port acts as the primary boundary between external systems and the chatbot application.
    It defines the contract for processing chat messages and generating responses, serving
    as the main entry point for all chat functionality in the system.

    The implementing adapters will handle the actual communication with external systems,
    while conforming to this interface.
    """

    @abstractmethod
    async def query(self, request: Query) -> Response:
        """Processes a chat message and returns a response.

        This is the main use case for chat interactions. It takes a Query object
        containing the user's message and context, processes it through the chatbot system,
        and returns an appropriate Response.

        Args:
            request (Query): The query object containing the user's message and any
                additional context needed for processing.

        Returns:
            Response: The chatbot's response to the user's message, which may include
                text, actions, or other response elements.

        Raises:
            TODO
        """
        pass
