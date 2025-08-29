from typing import List
import logging
import time
import uuid

from src.components.rag.application.ports.driven.event_bus_port import EventBusPort
from src.components.rag.application.ports.driving import QueryPort
from src.components.rag.domain.services.query_service import QueryService
from src.components.rag.domain.value_objects import DocumentRetrieval, RAGResponse, Query
from src.shared.domain.events.query_events import QueryRequestedEvent, QueryCompletedEvent

logger = logging.getLogger(__name__)

class QueryHandler(QueryPort):
    """Pure business logic for combining retrieval and LLM components.

    The QueryHandler class orchestrates the Retrieval-Augmented Generation process
    by combining document retrieval results with language model outputs to produce
    coherent responses with source attribution.

    This class implements the core RAG workflow logic without dependencies on
    specific retrieval or LLM implementations, following domain-driven design
    principles.
    """
    def __init__(self, query_service: QueryService, event_bus: EventBusPort = None):
        """
        Initialize QueryHandler.
        
        Args:
            query_service (QueryService): Service containing domain logic for query processing.
            event_bus (EventBusPort, optional): Event bus for publishing events.
        """
        self.service = query_service
        self.event_bus = event_bus
        logger.info("query_handler :: Initialized QueryHandler")
    
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
        logger.info("query_handler :: Processing query")
        start_time = time.time()
        
        # Generate a unique query ID
        query_id = str(uuid.uuid4())
        
        # Publish query requested event
        if self.event_bus:
            query_requested_event = QueryRequestedEvent.create(
                query_id=query_id,
                query_text=user_query.content,
                metadata={"component": "rag"}
            )
            await self.event_bus.publish_event(query_requested_event)
            logger.debug(f"query_handler :: Published query requested event with id: {query_requested_event.id}")
        
        # Process the query
        response = await self.service.process_query(query=user_query)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Publish query completed event
        if self.event_bus:
            # Extract document IDs from the response
            document_ids = [doc.id for doc in response.sources]
            
            query_completed_event = QueryCompletedEvent.create(
                query_id=query_id,
                response_text=response.content,
                document_ids=document_ids,
                processing_time=processing_time,
                metadata={
                    "component": "rag",
                    "model_used": response.model_used,
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens
                }
            )
            await self.event_bus.publish_event(query_completed_event)
            logger.debug(f"query_handler :: Published query completed event with id: {query_completed_event.id}")
        
        logger.info(f"query_handler :: Query processing completed in {processing_time:.2f} seconds")
        return response
