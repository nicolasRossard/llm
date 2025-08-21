from typing import List

from src.components.rag.domain.value_objects import DocumentRetrieval, RAGResponse, Query, Response


class RAGPipeline:
    """Pure business logic for combining retrieval and LLM components.

    The RAGPipeline class orchestrates the Retrieval-Augmented Generation process
    by combining document retrieval results with language model outputs to produce
    coherent responses with source attribution.

    This class implements the core RAG workflow logic without dependencies on
    specific retrieval or LLM implementations, following domain-driven design
    principles.
    """
    
    async def generate_response(self, user_query: Query, llm_output: Response, retrieved_chunks: List[DocumentRetrieval]) -> RAGResponse:
        """Generate a RAG response by combining LLM output with retrieved sources.
        
        Takes the output from a language model and combines it with the retrieved
        document chunks to create a complete RAG (Retrieval-Augmented Generation)
        response that includes both the generated content and source references.
        
        Args:
            query (Query): The user query object containing the search request.
            llm_output (Response): The response object from the language model
                containing the generated text and metadata.
            retrieved_chunks (List[DocumentRetrieval]): List of document chunks
                that were retrieved and used as context for the generation.
                
        Returns:
            RAGResponse: A complete RAG response containing the LLM output data
                along with the source document references.
        """

        return RAGResponse(
            content=llm_output.content,
            generated_at=llm_output.generated_at,
            model_used=llm_output.model_used,
            processing_time_ms=llm_output.processing_time_ms,
            input_tokens=llm_output.input_tokens,
            output_tokens=llm_output.output_tokens,
            sources=retrieved_chunks
        )
