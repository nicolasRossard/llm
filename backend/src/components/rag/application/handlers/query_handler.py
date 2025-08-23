from typing import List

from src.components.rag.application.ports.driving import QueryPort
from src.components.rag.domain.services.query_service import QueryService
from src.components.rag.domain.value_objects import DocumentRetrieval, RAGResponse, Query, Response


class QueryHandler(QueryPort):
    """Pure business logic for combining retrieval and LLM components.

    The RAGPipeline class orchestrates the Retrieval-Augmented Generation process
    by combining document retrieval results with language model outputs to produce
    coherent responses with source attribution.

    This class implements the core RAG workflow logic without dependencies on
    specific retrieval or LLM implementations, following domain-driven design
    principles.
    """
    def __init__(self, query_service: QueryService):
        self.service = query_service
    
    async def query(self, user_query: Query) -> RAGResponse:
        """Generate a RAG response by combining LLM output with retrieved sources.
        
        Takes the output from a language model and combines it with the retrieved
        document chunks to create a complete RAG (Retrieval-Augmented Generation)
        response that includes both the generated content and source references.
        
        Args:
            user_query (Query): The user query object containing the search request.
        Returns:
            RAGResponse: A complete RAG response containing the LLM output data
                along with the source document references.
        """

        return await self.service.process_query(query=user_query)
