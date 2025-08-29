import logging
import uuid
from typing import List, Optional

from src.components.rag.application.ports.driven import VectorRetrieverPort, LLMPort, EmbeddingPort
from src.components.rag.application.ports.driven.event_bus_port import EventBusPort
from src.components.rag.config import RAGConfig
from src.components.rag.domain.value_objects import Query, DocumentRetrieval, Message, RAGResponse, Embedding
from src.components.rag.domain.value_objects.message_role import MessageRole
from src.shared.domain.events.query_events import DocumentsRetrievedEvent


class QueryService:
    """Service for processing user queries using RAG."""

    def __init__(
            self,
            vector_retriever_port: VectorRetrieverPort,
            llm_port: LLMPort,
            embedding_port: EmbeddingPort,
            rag_config: RAGConfig,
            event_bus: Optional[EventBusPort] = None,
    ):
        """Initialize QueryService.

        Args:
            vector_retriever_port: Vector search interface.
            llm_port: LLM interface.
            embedding_port: Text embedding interface.
            rag_config: RAG configuration.
            event_bus: Optional event bus for publishing events.
        """
        self.rag_config = rag_config
        self.embedding_port = embedding_port
        self.vector_retriever_port = vector_retriever_port
        self.llm_port = llm_port
        self.event_bus = event_bus
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("query_service :: QueryService initialized successfully")

    async def _retrieve_relevant_documents(self, query_embedding: Embedding, query_id: str = None) -> List[DocumentRetrieval]:
        """Retrieve relevant documents using vector search.

        Args:
            query_embedding: Query embedding vector.
            query_id: Optional ID for the query (for event tracking).

        Returns:
            List of relevant documents.
        """
        self.logger.debug("query_service :: Starting document retrieval...")
        retrieved_documents = await self.vector_retriever_port.search(query=query_embedding.vector)
        self.logger.info(f"query_service :: Retrieved {len(retrieved_documents)} documents from vector search")
        self.logger.debug(f"query_service :: Retrieved document IDs: {[doc.id for doc in retrieved_documents]}")
        
        # Publish documents retrieved event if we have an event bus and query ID
        if self.event_bus and query_id:
            document_ids = [doc.id for doc in retrieved_documents]
            # Extract scores if available in the document metadata
            scores = [doc.metadata.get('score') for doc in retrieved_documents 
                     if doc.metadata and 'score' in doc.metadata]
            
            documents_retrieved_event = DocumentsRetrievedEvent.create(
                query_id=query_id,
                document_ids=document_ids,
                scores=scores if scores and len(scores) == len(document_ids) else None
            )
            await self.event_bus.publish_event(documents_retrieved_event)
            self.logger.debug(f"query_service :: Published documents retrieved event with id: {documents_retrieved_event.id}")
        
        return retrieved_documents

    async def _build_context_messages(self, user_query: str, retrieved_documents: List[DocumentRetrieval]) -> List[Message]:
        """Create LLM prompt with retrieved context.

        Args:
            user_query: User query text.
            retrieved_documents: Retrieved documents for context.

        Returns:
            Formatted messages for LLM.
        """
        self.logger.debug(f"query_service :: Building context messages for query: '{user_query[:100]}...'")
        context_content = "Here the context\n\n"
        context_content += "\n\n".join([f"Document {i+1}:\n{doc.content}" for i, doc in enumerate(retrieved_documents)])

        messages = [
            Message(role=MessageRole.SYSTEM, content=self.rag_config.system_prompt),
            Message(role=MessageRole.SYSTEM, content=context_content),
            Message(role=MessageRole.USER, content=user_query)
        ]

        self.logger.info(f"query_service :: Built context with {len(messages)} messages and {len(retrieved_documents)} documents")
        self.logger.debug(f"query_service :: Total context length: {len(context_content)} characters")
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
        self.logger.info("query_service :: Starting query processing")
        self.logger.debug(f"query_service :: Query content: '{query.content[:200]}...'")
        
        # Generate a query ID for tracking if we have an event bus
        query_id = str(uuid.uuid4()) if self.event_bus else None

        # Step 1: Validate the query
        validated_query = await self._validate_query(query)
        self.logger.debug("query_service :: Query validation completed successfully")

        # Step 2: Generate embedding for the query
        self.logger.debug("query_service :: Generating query embedding")
        query_embedding = await self.embedding_port.embed_text(validated_query.content)

        # Step 3: Retrieve relevant documents and build context messages
        retrieved_documents = await self._retrieve_relevant_documents(
            query_embedding=query_embedding, 
            query_id=query_id
        )
        
        context_messages = await self._build_context_messages(validated_query.content, retrieved_documents)

        # Step 4: Generate response from LLM
        self.logger.debug("query_service :: Sending request to LLM")
        llm_response = await self.llm_port.generate_response(context_messages)
        self.logger.info("query_service :: LLM response generated successfully")

        self.logger.info("query_service :: Query processing completed successfully")
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
