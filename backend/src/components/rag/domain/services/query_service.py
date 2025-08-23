import logging
from typing import List


from src.components.rag.application.ports.driven import VectorRetrieverPort, LLMPort, EmbeddingPort
from src.components.rag.config import RAGConfig
from src.components.rag.domain.value_objects import Query, DocumentRetrieval, Message, RAGResponse
from src.components.rag.domain.value_objects.message_role import MessageRole


class QueryService:
    """Service for processing user queries using RAG."""

    def __init__(
            self,
            vector_retriever_port: VectorRetrieverPort,
            llm_port: LLMPort,
            embedding_port: EmbeddingPort,
            rag_config: RAGConfig,
    ):
        """Initialize QueryService.

        Args:
            vector_retriever_port: Vector search interface.
            llm_port: LLM interface.
            embedding_port: Text embedding interface.
            rag_config: RAG configuration.
        """
        self.rag_config = rag_config
        self.embedding_port = embedding_port
        self.vector_retriever_port = vector_retriever_port
        self.llm_port = llm_port
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("QueryService initialized successfully")

    async def _retrieve_relevant_documents(self, query_embedding: list[float]) -> List[DocumentRetrieval]:
        """Retrieve relevant documents using vector search.

        Args:
            query_embedding: Query embedding vector.

        Returns:
            List of relevant documents.
        """
        self.logger.debug("Starting document retrieval ...")
        retrieved_documents = await self.vector_retriever_port.search(query_embedding)
        self.logger.info(f"Retrieved {len(retrieved_documents)} documents from vector search")
        self.logger.debug(f"Retrieved document IDs: {[doc.id for doc in retrieved_documents]}")
        return retrieved_documents

    async def _build_context_messages(self, user_query: str, retrieved_documents: List[DocumentRetrieval]) -> List[Message]:
        """Create LLM prompt with retrieved context.

        Args:
            user_query: User query text.
            retrieved_documents: Retrieved documents for context.

        Returns:
            Formatted messages for LLM.
        """
        self.logger.debug(f"Building context messages for query: '{user_query[:100]}...'")
        context_content = "Here the context\n\n"
        context_content += "\n\n".join([f"Document {i+1}:\n{doc.content}" for i, doc in enumerate(retrieved_documents)])

        messages = [
            Message(role=MessageRole.SYSTEM, content=self.rag_config.system_prompt),
            Message(role=MessageRole.SYSTEM, content=context_content),
            Message(role=MessageRole.USER, content=user_query)
        ]

        self.logger.info(f"Built context with {len(messages)} messages and {len(retrieved_documents)} documents")
        self.logger.debug(f"Total context length: {len(context_content)} characters")
        return messages

    @staticmethod
    async def _validate_query(query: Query) -> Query:
        """Validate query content.

        Args:
            query: Query to validate.

        Returns:
            Validated query.

        Raises:
            ValueError: If query content is empty.
        """
        if not query.content.strip():
            raise ValueError("Query content cannot be empty")
        return query

    async def process_query(self, query: Query) -> RAGResponse:
        """Process query to generate RAG response.

        Args:
            query: User query to process.

        Returns:
            Generated response with sources.
        """
        self.logger.info("Starting query processing for query")
        self.logger.debug(f"Query content: '{query.content[:200]}...'")

        # Step 1: Validate the query
        validated_query = await self._validate_query(query)
        self.logger.debug("Query validation completed successfully")

        # Step 2: Generate embedding for the query
        self.logger.debug("Generating query embedding")
        query_embedding = await self.embedding_port.embed_text(validated_query.content)

        # Step 3: Retrieve relevant documents and build context messages
        retrieved_documents = await self._retrieve_relevant_documents(query_embedding=query_embedding)
        
        context_messages = await self._build_context_messages(validated_query.content, retrieved_documents)

        # Step 4: Generate response from LLM
        self.logger.debug("Sending request to LLM")
        llm_response = await self.llm_port.generate_response(context_messages)
        self.logger.info("LLM response generated successfully")

        self.logger.info("Query processing completed successfully for query")
        # Step 5: Format and return RAG response
        return RAGResponse(
            content=llm_response.content,
            generated_at=llm_response.generated_at,
            model_used=llm_response.model_used,
            processing_time_ms=llm_response.processing_time_ms,
            input_tokens=llm_response.input_tokens,
            output_tokens=llm_response.output_tokens,
            sources=retrieved_documents
        )
