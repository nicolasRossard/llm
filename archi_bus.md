nicolasRossard: Tu es un expert architecture code maîtrisant les différents concepts
voici l'arborescence de mon projet actuel (dossier backend/)
```
backend/
├── config.py                  # Global configuration settings for the application
├── logs/                      # Application logs directory
├── main.py                    # Application entry point - initializes FastAPI and dependencies
├── src/
│   └── components/
│       └── rag/               # RAG component following hexagonal architecture
│           ├── application/   # Application layer
│           │   ├── handlers/  # Use case handlers implementing business logic
│           │   │              # (e.g., DocumentStoreHandler, QueryHandler)
│           │   └── ports/     # Interfaces defining how to interact with the application core
│           │       ├── driven/  # Interfaces that the application uses to communicate outward
│           │       │            # (e.g., EmbeddingPort, LLMPort, VectorStorePort)
│           │       └── driving/ # Interfaces that allow external systems to use the application
│           │                    # (e.g., DocumentStorePort, QueryPort)
│           ├── config/        # Component-specific configuration
│           │                  # (e.g., RAGConfig)
│           ├── domain/        # Domain layer - core business rules and concepts
│           │   ├── entities/  # Business objects with identity and lifecycle
│           │   │              # (e.g., QueryModel, RAGResponseModel)
│           │   ├── services/  # Domain services that operate on multiple entities
│           │   │              # (e.g., DocumentStoreService, QueryService)
│           │   └── value_objects/ # Immutable objects without identity
│           │                      # (e.g., Query, Embedding, Message, DocumentRetrieval)
│           ├── infrastructure/ # Infrastructure layer - technical details and implementations
│           │   ├── adapters/  # Connect the application to external systems
│           │   │   ├── driven/ # Implementations of ports the application uses
│           │   │   │           # (e.g., LiteLLMAdapter, DoclingAdapter)
│           │   │   └── driving/ # Implementations of ports to drive the application
│           │   ├── api/       # API definition and routing
│           │   │   ├── di/    # Dependency Injection configuration
│           │   │   └── v1/    # API version 1
│           │   │       ├── dto.py        # Data Transfer Objects for API requests/responses
│           │   │       └── rag_routes.py # FastAPI route definitions for RAG
│           │   └── persistence/ # Repository implementations and data access
│           │                    # (e.g., QdrantVectorStoreAdapter, QdrantVectorRetrieverAdapter)
│           └── tests/         # Test files following the same structure as source code
└── uvicorn_debug.py          # Script for running the app in debug mode with uvicorn
```
J'ai essayé de créer une architecture hexagonale Domain Driven design basé sur les notes tout en séparant en composant.

J'aimerais échanger avec toi sur la création d'une base de donnée de tracking permettant de :
Stocker les fichiers chargés dans le rag (base non vectorielle)
Tracker l'activité des use cases (query ou document store)

# problématiques identifiés :
* On rajoute de la complexité donc la lisibilité du service qui devait être la logique business va être touché
* On doit combiner à certains moment base de données vectorielle et base de données (exemple on doit créer l'ID en BDD et l'ajouter dans la partie metadonnée de la base vectorielle pour faciliter sa suppression plus tard)

A partir de là propose moi une architecture code en mettant à jour l'arborescence de fichiers présentés précédement.

Dans ta nouvelle arborescence, Tu dois être en mesure de répondre à ces questions :
* où mettre la logique business avec juste les actions "métiers"
* Comment cohabiter les différents bases de données
* Comment garder une architecture hexagonale Domain driven design ?
* Comment conserver la partie atomique des ports
* est-ce que la partie tracking est un composant à part ?

GitHub Copilot: # Tracking Database Architecture in Hexagonal DDD

Looking at your current architecture, I'll propose an approach to integrate tracking capabilities while maintaining hexagonal architecture principles and DDD best practices.

## Architecture Analysis

Your existing architecture follows hexagonal architecture well, with clear separation of:
- Domain layer (core business logic)
- Application layer (use cases, ports)
- Infrastructure layer (adapters, API, persistence)

## Proposed Solution

The best approach is to treat tracking as a **separate component** with its own hexagonal architecture, while enabling communication between components through domain events.

### Updated File Structure

```
backend/
├── config.py                  # Global configuration settings
├── logs/                      # Application logs directory
├── main.py                    # Application entry point
├── src/
│   ├── shared/                # Shared kernel between components
│   │   ├── domain/
│   │   │   ├── events/        # Domain events definitions
│   │   │   │   ├── document_events.py  # Document-related events
│   │   │   │   └── query_events.py     # Query-related events
│   │   │   └── value_objects/ # Shared value objects
│   │   │       └── id.py      # Shared ID generation strategy
│   │   └── infrastructure/
│   │       └── event_bus/     # Event dispatcher implementation
│   │           ├── event_bus.py
│   │           └── interfaces.py
│   │
│   └── components/
│       ├── rag/               # RAG component (mostly unchanged)
│       │   ├── application/
│       │   │   ├── handlers/
│       │   │   │   ├── document_store_handler.py
│       │   │   │   └── query_handler.py
│       │   │   └── ports/
│       │   │       ├── driven/
│       │   │       │   ├── embedding_port.py
│       │   │       │   ├── event_bus_port.py  # NEW: For publishing events
│       │   │       │   ├── llm_port.py
│       │   │       │   └── vector_store_port.py
│       │   │       └── driving/
│       │   │           ├── document_store_port.py
│       │   │           └── query_port.py
│       │   ├── config/
│       │   │   └── rag_config.py
│       │   ├── domain/
│       │   │   ├── entities/
│       │   │   ├── services/
│       │   │   │   ├── document_store_service.py
│       │   │   │   └── query_service.py
│       │   │   └── value_objects/
│       │   ├── infrastructure/
│       │   │   ├── adapters/
│       │   │   │   ├── driven/
│       │   │   │   │   ├── event_bus_adapter.py  # NEW: Adapter for event bus
│       │   │   │   │   └── ... (other adapters)
│       │   │   │   └── driving/
│       │   │   ├── api/
│       │   │   └── persistence/
│       │   │       └── qdrant_vector_store_adapter.py
│       │   └── tests/
│       │
│       └── tracking/          # NEW: Tracking component
│           ├── application/
│           │   ├── handlers/
│           │   │   ├── document_tracking_handler.py
│           │   │   └── query_tracking_handler.py
│           │   └── ports/
│           │       ├── driven/
│           │       │   ├── document_repository_port.py
│           │       │   ├── event_bus_port.py      # For subscribing to events
│           │       │   └── query_repository_port.py
│           │       └── driving/
│           │           └── tracking_port.py       # For direct tracking access
│           ├── config/
│           │   └── tracking_config.py
│           ├── domain/
│           │   ├── entities/
│           │   │   ├── document_metadata.py       # Document tracking entity
│           │   │   └── query_log.py               # Query tracking entity
│           │   ├── services/
│           │   │   ├── document_tracking_service.py
│           │   │   └── query_tracking_service.py
│           │   └── value_objects/
│           │       └── tracking_id.py
│           ├── infrastructure/
│           │   ├── adapters/
│           │   │   ├── driven/
│           │   │   │   ├── event_bus_adapter.py   # Listens for events from RAG
│           │   │   │   └── sql_repository_adapter.py
│           │   │   └── driving/
│           │   │       └── tracking_api_adapter.py
│           │   ├── api/
│           │   │   └── v1/
│           │   │       ├── dto.py
│           │   │       └── tracking_routes.py
│           │   └── persistence/
│           │       ├── models/                    # ORM models
│           │       │   ├── document_model.py
│           │       │   └── query_log_model.py
│           │       └── repositories/
│           │           ├── document_repository.py
│           │           └── query_repository.py
│           └── tests/
└── uvicorn_debug.py
```

## Addressing Your Questions

### 1. Where to place business logic with just "business" actions?

- **Domain Services**: Pure business logic that operates on entities and value objects
  - `document_store_service.py` - Core document handling logic
  - `query_service.py` - Core query processing logic
  - `document_tracking_service.py` - Document tracking business rules
  - `query_tracking_service.py` - Query tracking business rules

- **Application Handlers**: Orchestration of use cases
  - `document_store_handler.py` - Coordinates document operations and publishes events
  - `query_handler.py` - Coordinates query operations and publishes events
  - `document_tracking_handler.py` - Reacts to document events
  - `query_tracking_handler.py` - Reacts to query events

### 2. How to handle multiple databases?

- **Separate Ports and Adapters**: Each database has its own port/adapter pair
  - RAG component: `vector_store_port.py` and `qdrant_vector_store_adapter.py`
  - Tracking component: `document_repository_port.py`, `query_repository_port.py` and `sql_repository_adapter.py`

- **Coordination**: Using the shared ID strategy from the shared kernel
  ```python
  # Example flow:
  # 1. Generate ID in shared service
  # 2. Store document in tracking DB
  # 3. Store document in vector DB with the same ID
  ```

### 3. How to maintain hexagonal architecture and DDD principles?

- **Clear Boundaries**: Each component has its own complete hexagonal structure
- **Domain Events**: Components communicate through events, not direct calls
- **Shared Kernel**: Minimal shared code between components
- **Ubiquitous Language**: Domain-specific terminology throughout

### 4. How to preserve atomic ports?

- **Focused Ports**: Each port has a single responsibility
- **Event-Based Communication**: Use events for cross-component coordination
- **Independent Adapters**: Each port has adapters tailored to specific technology

### 5. Is tracking a separate component?

**Yes** - Tracking should be a separate component because:
- It has its own domain logic and persistence needs
- It evolves at a different rate than RAG functionality
- It can be maintained, tested, and deployed independently
- It avoids cluttering the RAG component with tracking concerns

## Implementation Strategy

1. Create the shared kernel first with event interfaces
2. Enhance the RAG component to emit events
3. Implement the tracking component to consume these events
4. Establish the database coordination strategy

This architecture maintains clean hexagonal principles while addressing the complexity of coordinating between vector and relational databases.

nicolasRossard: ok avançons par étape :
Mise en place des events pour le projet rag actuel
quel serait les fichiers à créer en python et le docker compose on ajouterait pas une pile redis ?
Donne moi les noms des fichiers à créer et où et ce qu'ils font pas le code

GitHub Copilot: # Event System Implementation for RAG Project

To implement an event-driven architecture for your RAG project, here's what we need to create:

## Docker Compose Addition

First, let's add Redis to the docker-compose.yml as our event broker:

```yaml
redis:
  container_name: "rag_event_broker"
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - ./redis_data:/data
  command: redis-server --appendonly yes
  networks:
    - llm_net
```

## Files to Create

### Shared Kernel

1. **`/src/shared/domain/events/base_event.py`**
   - Base event class with common properties (id, timestamp, type)
   - Used as parent for all domain events

2. **`/src/shared/domain/events/document_events.py`**
   - Events for document lifecycle (DocumentCreated, DocumentUpdated, DocumentDeleted)
   - Contains payload schemas for document-related events

3. **`/src/shared/domain/events/query_events.py`**
   - Events for query execution (QueryRequested, QueryCompleted)
   - Contains payload schemas for query-related events

4. **`/src/shared/domain/value_objects/id.py`**
   - Shared ID generation strategy for consistent IDs across components

5. **`/src/shared/infrastructure/event_bus/interfaces.py`**
   - Defines EventBus interface with publish/subscribe methods
   - Defines EventHandler interface for event subscribers

6. **`/src/shared/infrastructure/event_bus/redis_event_bus.py`**
   - Redis implementation of the EventBus interface
   - Handles serialization/deserialization of events
   - Manages Redis pub/sub connections

### RAG Component Updates

7. **`/src/components/rag/application/ports/driven/event_bus_port.py`**
   - Interface defining how RAG component publishes events
   - Methods for publishing document and query events

8. **`/src/components/rag/infrastructure/adapters/driven/event_bus_adapter.py`**
   - Implementation of the event bus port using the shared Redis event bus
   - Connects RAG component to the event system

9. **Updates to existing handlers:**
   - `document_store_handler.py`: Add event publishing for document operations
   - `query_handler.py`: Add event publishing for query operations

### Event Handling Service

10. **`/src/components/tracking/application/ports/driven/event_bus_port.py`**
    - Interface for subscribing to events in the tracking component
    - Methods for registering event handlers

11. **`/src/components/tracking/infrastructure/adapters/driven/event_bus_adapter.py`**
    - Implementation of the event subscription port
    - Connects to Redis and routes events to appropriate handlers

12. **`/src/components/tracking/application/handlers/document_tracking_handler.py`**
    - Handles document events (creation, updates, deletion)
    - Updates tracking database accordingly

13. **`/src/components/tracking/application/handlers/query_tracking_handler.py`**
    - Handles query events (requests, completions)
    - Records query activity in tracking database

14. **`/src/components/tracking/infrastructure/persistence/models/document_model.py`**
    - ORM model for tracking document metadata
    - Maps to document tracking table in database

15. **`/src/components/tracking/infrastructure/persistence/models/query_log_model.py`**
    - ORM model for tracking query activity
    - Maps to query log table in database

## Implementation Process

1. First create the shared kernel with event definitions
2. Add Redis to your docker-compose and test it
3. Implement the event bus with Redis
4. Update the RAG component to publish events
5. Create the tracking component to consume events

This approach follows hexagonal architecture principles while enabling communication between components through an event-driven pattern.

nicolasRossard: fait l'étape 1

GitHub Copilot: # Implementation of the Shared Kernel with Event Definitions

Let's implement the first step - creating the shared kernel with event definitions. I'll create the necessary files and provide the code for each.

## 1. Creating the Directory Structure

First, let's create the required directory structure:

```bash
mkdir -p src/shared/domain/events
mkdir -p src/shared/domain/value_objects
mkdir -p src/shared/infrastructure/event_bus
```

## 2. Implementing the Shared Kernel Files

### File 1: `/src/shared/domain/events/base_event.py`

```python
"""Base event module providing foundation for domain events."""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseEvent(BaseModel):
    """
    Base class for all domain events.
    
    Provides common attributes and behavior for events throughout the system.
    """
    model_config = ConfigDict(frozen=True)
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the event"
    )
    event_type: str = Field(
        ..., 
        description="Type of the event (e.g., 'document.created', 'query.completed')"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the event occurred"
    )
    payload: Dict[str, Any] = Field(
        ...,
        description="Event data specific to each event type"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional contextual information about the event"
    )
```

### File 2: `/src/shared/domain/events/document_events.py`

```python
"""Document-related domain events module."""

from typing import Dict, List, Optional, Any

from pydantic import Field

from src.shared.domain.events.base_event import BaseEvent


class DocumentCreatedEvent(BaseEvent):
    """
    Event emitted when a new document is created in the system.
    """
    event_type: str = Field(
        "document.created",
        const=True,
        description="Indicates a document creation event"
    )
    payload: Dict[str, Any] = Field(
        ...,
        description="Document creation data"
    )
    
    @classmethod
    def create(
        cls, 
        document_id: str, 
        title: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> "DocumentCreatedEvent":
        """
        Create a document created event.
        
        Args:
            document_id (str): Unique identifier for the document.
            title (str): Title of the document.
            content (str): Content of the document.
            metadata (Optional[Dict[str, Any]]): Additional document metadata.
            
        Returns:
            DocumentCreatedEvent: A new document created event.
        """
        return cls(
            payload={
                "document_id": document_id,
                "title": title,
                "content": content,
                "metadata": metadata or {}
            }
        )


class DocumentUpdatedEvent(BaseEvent):
    """
    Event emitted when an existing document is updated.
    """
    event_type: str = Field(
        "document.updated",
        const=True,
        description="Indicates a document update event"
    )
    payload: Dict[str, Any] = Field(
        ...,
        description="Document update data"
    )
    
    @classmethod
    def create(
        cls, 
        document_id: str, 
        title: Optional[str] = None, 
        content: Optional[str] = None, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> "DocumentUpdatedEvent":
        """
        Create a document updated event.
        
        Args:
            document_id (str): Unique identifier for the document.
            title (Optional[str]): Updated title of the document.
            content (Optional[str]): Updated content of the document.
            metadata (Optional[Dict[str, Any]]): Updated document metadata.
            
        Returns:
            DocumentUpdatedEvent: A new document updated event.
        """
        payload = {"document_id": document_id}
        if title is not None:
            payload["title"] = title
        if content is not None:
            payload["content"] = content
        if metadata is not None:
            payload["metadata"] = metadata
            
        return cls(payload=payload)


class DocumentDeletedEvent(BaseEvent):
    """
    Event emitted when a document is deleted from the system.
    """
    event_type: str = Field(
        "document.deleted",
        const=True,
        description="Indicates a document deletion event"
    )
    payload: Dict[str, Any] = Field(
        ...,
        description="Document deletion data"
    )
    
    @classmethod
    def create(cls, document_id: str) -> "DocumentDeletedEvent":
        """
        Create a document deleted event.
        
        Args:
            document_id (str): Unique identifier for the deleted document.
            
        Returns:
            DocumentDeletedEvent: A new document deleted event.
        """
        return cls(payload={"document_id": document_id})


class DocumentsIngestedEvent(BaseEvent):
    """
    Event emitted when a batch of documents is ingested into the system.
    """
    event_type: str = Field(
        "documents.ingested",
        const=True,
        description="Indicates a document batch ingestion event"
    )
    payload: Dict[str, Any] = Field(
        ...,
        description="Document ingestion data"
    )
    
    @classmethod
    def create(cls, document_ids: List[str], batch_id: Optional[str] = None) -> "DocumentsIngestedEvent":
        """
        Create a documents ingested event.
        
        Args:
            document_ids (List[str]): List of document IDs that were ingested.
            batch_id (Optional[str]): Identifier for the ingestion batch.
            
        Returns:
            DocumentsIngestedEvent: A new documents ingested event.
        """
        return cls(
            payload={
                "document_ids": document_ids,
                "batch_id": batch_id,
                "count": len(document_ids)
            }
        )
```

### File 3: `/src/shared/domain/events/query_events.py`

```python
"""Query-related domain events module."""

from typing import Dict, List, Optional, Any

from pydantic import Field

from src.shared.domain.events.base_event import BaseEvent


class QueryRequestedEvent(BaseEvent):
    """
    Event emitted when a query is requested by a user.
    """
    event_type: str = Field(
        "query.requested",
        const=True,
        description="Indicates a query request event"
    )
    payload: Dict[str, Any] = Field(
        ...,
        description="Query request data"
    )
    
    @classmethod
    def create(
        cls, 
        query_id: str, 
        query_text: str, 
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "QueryRequestedEvent":
        """
        Create a query requested event.
        
        Args:
            query_id (str): Unique identifier for the query.
            query_text (str): The query text submitted by the user.
            user_id (Optional[str]): Identifier of the user making the query.
            metadata (Optional[Dict[str, Any]]): Additional query metadata.
            
        Returns:
            QueryRequestedEvent: A new query requested event.
        """
        return cls(
            payload={
                "query_id": query_id,
                "query_text": query_text,
                "user_id": user_id,
                "metadata": metadata or {}
            }
        )


class DocumentsRetrievedEvent(BaseEvent):
    """
    Event emitted when documents are retrieved during query processing.
    """
    event_type: str = Field(
        "documents.retrieved",
        const=True,
        description="Indicates a document retrieval event"
    )
    payload: Dict[str, Any] = Field(
        ...,
        description="Document retrieval data"
    )
    
    @classmethod
    def create(
        cls, 
        query_id: str, 
        document_ids: List[str], 
        scores: Optional[List[float]] = None
    ) -> "DocumentsRetrievedEvent":
        """
        Create a documents retrieved event.
        
        Args:
            query_id (str): Identifier of the query that triggered the retrieval.
            document_ids (List[str]): List of retrieved document IDs.
            scores (Optional[List[float]]): Relevance scores for the retrieved documents.
            
        Returns:
            DocumentsRetrievedEvent: A new documents retrieved event.
        """
        payload = {
            "query_id": query_id,
            "document_ids": document_ids,
            "count": len(document_ids),
        }
        
        if scores:
            payload["scores"] = scores
            
        return cls(payload=payload)


class QueryCompletedEvent(BaseEvent):
    """
    Event emitted when a query is fully processed and answered.
    """
    event_type: str = Field(
        "query.completed",
        const=True,
        description="Indicates a query completion event"
    )
    payload: Dict[str, Any] = Field(
        ...,
        description="Query completion data"
    )
    
    @classmethod
    def create(
        cls, 
        query_id: str, 
        response_text: str, 
        document_ids: List[str],
        processing_time: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "QueryCompletedEvent":
        """
        Create a query completed event.
        
        Args:
            query_id (str): Identifier of the completed query.
            response_text (str): The generated response text.
            document_ids (List[str]): IDs of documents used in the response.
            processing_time (float): Time taken to process the query (in seconds).
            metadata (Optional[Dict[str, Any]]): Additional response metadata.
            
        Returns:
            QueryCompletedEvent: A new query completed event.
        """
        return cls(
            payload={
                "query_id": query_id,
                "response_text": response_text,
                "document_ids": document_ids,
                "document_count": len(document_ids),
                "processing_time": processing_time,
                "metadata": metadata or {}
            }
        )
```

### File 4: `/src/shared/domain/value_objects/id.py`

```python
"""ID generation and management for consistent entity identification."""

import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ID(BaseModel):
    """
    Value object representing a unique identifier.
    
    Provides consistent ID generation across components.
    """
    model_config = ConfigDict(frozen=True)
    
    value: str = Field(
        ..., 
        description="The unique identifier string"
    )
    
    @classmethod
    def generate(cls) -> "ID":
        """
        Generate a new unique ID.
        
        Returns:
            ID: A new unique ID instance.
        """
        return cls(value=str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, id_string: str) -> "ID":
        """
        Create an ID from an existing string.
        
        Args:
            id_string (str): Existing ID string to wrap.
            
        Returns:
            ID: An ID instance wrapping the provided string.
        """
        return cls(value=id_string)
    
    def __str__(self) -> str:
        """
        Convert ID to string.
        
        Returns:
            str: String representation of the ID.
        """
        return self.value
```

### File 5: `/src/shared/infrastructure/event_bus/interfaces.py`

```python
"""Interfaces for the event bus system."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Type, TypeVar

from src.shared.domain.events.base_event import BaseEvent

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseEvent)
EventHandler = Callable[[BaseEvent], None]


class EventBus(ABC):
    """
    Interface for event bus implementations.
    
    Defines methods for publishing and subscribing to events.
    """
    
    @abstractmethod
    def publish(self, event: BaseEvent) -> None:
        """
        Publish an event to the event bus.
        
        Args:
            event (BaseEvent): The event to publish.
        """
        pass
    
    @abstractmethod
    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """
        Subscribe a handler to a specific event type.
        
        Args:
            event_type (str): The type of event to subscribe to.
            handler (EventHandler): The function to call when the event occurs.
        """
        pass
    
    @abstractmethod
    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """
        Unsubscribe a handler from a specific event type.
        
        Args:
            event_type (str): The type of event to unsubscribe from.
            handler (EventHandler): The handler to remove.
        """
        pass
    
    @abstractmethod
    def start(self) -> None:
        """
        Start the event bus, beginning to process events.
        """
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """
        Stop the event bus, ceasing to process events.
        """
        pass


class EventPublisher(ABC):
    """
    Interface for components that publish events.
    
    A simplified interface focused solely on publishing events.
    """
    
    @abstractmethod
    def publish_event(self, event: BaseEvent) -> None:
        """
        Publish an event to the event bus.
        
        Args:
            event (BaseEvent): The event to publish.
        """
        pass


class EventSubscriber(ABC):
    """
    Interface for components that subscribe to events.
    
    Defines methods for registering event handlers.
    """
    
    @abstractmethod
    def register_handler(self, event_type: str, handler: EventHandler) -> None:
        """
        Register a handler for a specific event type.
        
        Args:
            event_type (str): The type of event to handle.
            handler (EventHandler): The function to call when the event occurs.
        """
        pass
    
    @abstractmethod
    def start_listening(self) -> None:
        """
        Start listening for events.
        """
        pass
    
    @abstractmethod
    def stop_listening(self) -> None:
        """
        Stop listening for events.
        """
        pass
```

This completes step 1 - creating the shared kernel with event definitions. These files establish the foundation for the event-driven architecture in your RAG project, defining the event types, ID generation, and interfaces for the event bus system.

nicolasRossard: ok step 2

GitHub Copilot: # Step 2: Add Redis to Docker Compose and Implement Event Bus

For this step, we'll add Redis to the docker-compose.yml file and implement the Redis event bus adapter.

## 1. Updating Docker Compose

Let's add Redis to your docker-compose.yml:

```yaml
name: 'ollama-open-webui'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    pull_policy: always
    tty: true
    restart: unless-stopped
    ports:
      - 11434:11434
    volumes:
      - ./ollama_data:/root/.ollama
      - ./ollama_entrypoint.sh:/entrypoint.sh
    environment:
      - 'OLLAMA_MAX_LOADED_MODELS=4'
      - 'OLLAMA_NUM_PARALLEL=1'
      - 'OLLAMA_KEEP_ALIVE=-1'
    entrypoint: ["/entrypoint.sh"]
    deploy:
      resources:
        limits:
          memory: 10G
    networks:
      - llm_net

  qdrant:
    container_name: "rag_personal_vector_db"
    restart: on-failure
    image: qdrant/qdrant:v1.13.3
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./qdrant_storage:/qdrant/storage:z
    networks:
      - llm_net
      
  redis:
    container_name: "rag_event_broker"
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - ./redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped
    networks:
      - llm_net

networks:
  llm_net:
    external: true
```

## 2. Implementing the Redis Event Bus

Now, let's create the Redis implementation of the event bus:

```python
"""Redis implementation of the event bus for publishing and subscribing to events."""

import json
import logging
import threading
import time
from typing import Any, Callable, Dict, List, Optional

import redis

from src.shared.domain.events.base_event import BaseEvent
from src.shared.infrastructure.event_bus.interfaces import EventBus, EventHandler

logger = logging.getLogger(__name__)


class RedisEventBus(EventBus):
    """
    Redis implementation of the event bus.
    
    Uses Redis pub/sub mechanism for event distribution.
    """
    
    def __init__(
        self, 
        redis_host: str = "localhost", 
        redis_port: int = 6379, 
        redis_db: int = 0,
        channel_prefix: str = "events:"
    ):
        """
        Initialize Redis event bus.
        
        Args:
            redis_host (str): Redis server hostname. Defaults to "localhost".
            redis_port (int): Redis server port. Defaults to 6379.
            redis_db (int): Redis database number. Defaults to 0.
            channel_prefix (str): Prefix for Redis channels. Defaults to "events:".
        """
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.channel_prefix = channel_prefix
        
        # Publisher connection
        self.publisher = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True
        )
        
        # Subscriber connection (separate from publisher to avoid blocking)
        self.subscriber = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True
        )
        self.pubsub = self.subscriber.pubsub(ignore_subscribe_messages=True)
        
        # Event handlers mapping
        self.handlers: Dict[str, List[EventHandler]] = {}
        
        # Thread for processing messages
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        logger.info("redis_event_bus :: Initialized RedisEventBus")
    
    def publish(self, event: BaseEvent) -> None:
        """
        Publish an event to the event bus.
        
        Args:
            event (BaseEvent): The event to publish.
        """
        channel = f"{self.channel_prefix}{event.event_type}"
        event_json = event.model_dump_json()
        
        try:
            self.publisher.publish(channel, event_json)
            logger.debug(f"redis_event_bus :: Published event {event.event_type} with id {event.id}")
        except Exception as e:
            logger.error(f"redis_event_bus :: Error publishing event: {e}")
            raise
    
    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """
        Subscribe a handler to a specific event type.
        
        Args:
            event_type (str): The type of event to subscribe to.
            handler (EventHandler): The function to call when the event occurs.
        """
        channel = f"{self.channel_prefix}{event_type}"
        
        # Add handler to internal mapping
        if event_type not in self.handlers:
            self.handlers[event_type] = []
            # Subscribe to the channel if this is the first handler
            self.pubsub.subscribe(channel)
            logger.info(f"redis_event_bus :: Subscribed to channel {channel}")
        
        self.handlers[event_type].append(handler)
        logger.debug(f"redis_event_bus :: Added handler for event type {event_type}")
    
    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """
        Unsubscribe a handler from a specific event type.
        
        Args:
            event_type (str): The type of event to unsubscribe from.
            handler (EventHandler): The handler to remove.
        """
        if event_type in self.handlers and handler in self.handlers[event_type]:
            self.handlers[event_type].remove(handler)
            logger.debug(f"redis_event_bus :: Removed handler for event type {event_type}")
            
            # Unsubscribe from the channel if no handlers remain
            if not self.handlers[event_type]:
                channel = f"{self.channel_prefix}{event_type}"
                self.pubsub.unsubscribe(channel)
                del self.handlers[event_type]
                logger.info(f"redis_event_bus :: Unsubscribed from channel {channel}")
    
    def _handle_message(self, message: Dict[str, Any]) -> None:
        """
        Handle a received message from Redis.
        
        Args:
            message (Dict[str, Any]): The message received from Redis.
        """
        if not message or message.get('type') != 'message':
            return
        
        channel = message.get('channel', '')
        if not channel.startswith(self.channel_prefix):
            return
        
        event_type = channel[len(self.channel_prefix):]
        if event_type not in self.handlers:
            return
        
        try:
            # Parse the event data
            event_data = json.loads(message.get('data', '{}'))
            
            # Call all registered handlers
            for handler in self.handlers[event_type]:
                try:
                    handler(event_data)
                except Exception as e:
                    logger.error(f"redis_event_bus :: Error in event handler: {e}")
        except json.JSONDecodeError:
            logger.error(f"redis_event_bus :: Invalid JSON in message: {message.get('data')}")
        except Exception as e:
            logger.error(f"redis_event_bus :: Error processing message: {e}")
    
    def _message_listener(self) -> None:
        """
        Background thread that listens for messages from Redis.
        """
        logger.info("redis_event_bus :: Starting message listener thread")
        
        while self.running:
            try:
                message = self.pubsub.get_message(timeout=1.0)
                if message:
                    self._handle_message(message)
                time.sleep(0.01)  # Small sleep to prevent CPU hogging
            except redis.RedisError as e:
                logger.error(f"redis_event_bus :: Redis error in listener thread: {e}")
                time.sleep(1)  # Wait before retry
            except Exception as e:
                logger.error(f"redis_event_bus :: Unexpected error in listener thread: {e}")
                time.sleep(1)  # Wait before retry
    
    def start(self) -> None:
        """
        Start the event bus, beginning to process events.
        """
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._message_listener, daemon=True)
        self.thread.start()
        logger.info("redis_event_bus :: Event bus started")
    
    def stop(self) -> None:
        """
        Stop the event bus, ceasing to process events.
        """
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
        
        # Clean up Redis connections
        self.pubsub.close()
        self.subscriber.close()
        self.publisher.close()
        
        logger.info("redis_event_bus :: Event bus stopped")
```

## 3. Create Config File for Redis Settings

Let's also create a configuration file for Redis settings:

```python
"""Configuration for the event bus system."""

from pydantic import BaseModel, Field


class RedisConfig(BaseModel):
    """
    Configuration for Redis event bus.
    
    Contains connection settings and operational parameters.
    """
    host: str = Field(
        default="localhost",
        description="Redis server hostname"
    )
    port: int = Field(
        default=6379,
        description="Redis server port"
    )
    db: int = Field(
        default=0,
        description="Redis database number"
    )
    channel_prefix: str = Field(
        default="events:",
        description="Prefix for Redis channels used by the event bus"
    )
    password: str = Field(
        default="",
        description="Redis server password (if required)"
    )
    ssl: bool = Field(
        default=False,
        description="Whether to use SSL for Redis connection"
    )
```

This completes Step 2 of implementing the event system. We've added Redis to the docker-compose.yml file and created the Redis-based implementation of the event bus interface.

nicolasRossard: fais les étapes :
* Implement the event bus with Redis
* Update the RAG component to publish events

focalise toi sur la partie query uniquement et en regardant l'existant et analyse le code de façon plus poussée

GitHub Copilot: # Implementing Event Bus with Redis for Query Tracking

Based on the code you've provided, I'll implement the event system for the RAG component, focusing specifically on the query flow. This implementation will allow tracking of query events through Redis.

## Step 1: Create Event Bus Port for the RAG Component

First, let's create a port interface for the event bus within the RAG component:

```python
"""Event bus port for publishing events from RAG component."""

from abc import ABC, abstractmethod

from src.shared.domain.events.base_event import BaseEvent


class EventBusPort(ABC):
    """
    Port interface for publishing events from the RAG component.
    
    Defines how the RAG component can publish domain events to the event bus.
    """
    
    @abstractmethod
    async def publish_event(self, event: BaseEvent) -> None:
        """
        Publish an event to the event bus.
        
        Args:
            event (BaseEvent): The event to publish.
        """
        pass
```

## Step 2: Create Event Bus Adapter for Redis

Now, let's implement the adapter that connects the RAG component to the Redis event bus:

```python
"""Redis event bus adapter for the RAG component."""

import logging
from typing import Optional

from src.components.rag.application.ports.driven.event_bus_port import EventBusPort
from src.shared.domain.events.base_event import BaseEvent
from src.shared.infrastructure.event_bus.redis_event_bus import RedisEventBus

logger = logging.getLogger(__name__)


class RedisEventBusAdapter(EventBusPort):
    """
    Adapter that connects the RAG component to the Redis event bus.
    
    Implements the EventBusPort interface using the Redis event bus.
    """
    
    def __init__(
        self, 
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        event_bus: Optional[RedisEventBus] = None
    ):
        """
        Initialize Redis event bus adapter.
        
        Args:
            redis_host (str): Redis server hostname. Defaults to "localhost".
            redis_port (int): Redis server port. Defaults to 6379.
            redis_db (int): Redis database number. Defaults to 0.
            event_bus (Optional[RedisEventBus]): Existing event bus instance to use.
                If None, a new instance will be created.
        """
        self.event_bus = event_bus or RedisEventBus(
            redis_host=redis_host,
            redis_port=redis_port,
            redis_db=redis_db
        )
        # Ensure the event bus is started
        self.event_bus.start()
        logger.info("event_bus_adapter :: Initialized RedisEventBusAdapter")
    
    async def publish_event(self, event: BaseEvent) -> None:
        """
        Publish an event to the Redis event bus.
        
        Args:
            event (BaseEvent): The event to publish.
        """
        logger.info(f"event_bus_adapter :: Publishing event: {event.event_type}")
        logger.debug(f"event_bus_adapter :: Event details - id: {event.id}, payload: {event.payload}")
        self.event_bus.publish(event)
        logger.debug(f"event_bus_adapter :: Event published successfully: {event.id}")
```

## Step 3: Update QueryHandler to Publish Events

Now, let's modify the QueryHandler to publish events at key points in the flow:

```python
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
```

## Step 4: Update QueryService to Publish Document Retrieval Events

Now, let's modify the QueryService to publish events when documents are retrieved:

```python
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
```

## Step 5: Update Dependency Injection for Event Bus

Finally, let's update the dependency injection to provide the event bus to our handlers:

```python
"""Dependency injection for query components."""

import logging
from functools import lru_cache

from fastapi import Depends

from src.components.rag.application.handlers.query_handler import QueryHandler
from src.components.rag.application.ports.driven import LLMPort, VectorRetrieverPort, EmbeddingPort
from src.components.rag.application.ports.driven.event_bus_port import EventBusPort
from src.components.rag.config import get_rag_config
from src.components.rag.domain.services.query_service import QueryService
from src.components.rag.infrastructure.adapters.driven.event_bus_adapter import RedisEventBusAdapter
from src.components.rag.infrastructure.adapters.driven.litellm_adapter import LiteLLMAdapter
from src.components.rag.infrastructure.adapters.driven.litellm_embedding_adapter import LiteLLMEmbeddingAdapter
from src.components.rag.infrastructure.persistence.qdrant_vector_retriever_adapter import QdrantVectorRetrieverAdapter

logger = logging.getLogger(__name__)


@lru_cache
def get_vector_retriever() -> VectorRetrieverPort:
    """
    Get the vector retriever implementation.
    
    Returns:
        VectorRetrieverPort: Vector retriever implementation.
    """
    logger.debug("query_di :: Creating vector retriever")
    return QdrantVectorRetrieverAdapter()


@lru_cache
def get_llm() -> LLMPort:
    """
    Get the LLM implementation.
    
    Returns:
        LLMPort: LLM implementation.
    """
    logger.debug("query_di :: Creating LLM adapter")
    return LiteLLMAdapter()


@lru_cache
def get_embedding() -> EmbeddingPort:
    """
    Get the embedding implementation.
    
    Returns:
        EmbeddingPort: Embedding implementation.
    """
    logger.debug("query_di :: Creating embedding adapter")
    return LiteLLMEmbeddingAdapter()


@lru_cache
def get_event_bus() -> EventBusPort:
    """
    Get the event bus implementation.
    
    Returns:
        EventBusPort: Event bus implementation.
    """
    logger.debug("query_di :: Creating event bus adapter")
    return RedisEventBusAdapter(redis_host="rag_event_broker")


@lru_cache
def get_query_service(
    vector_retriever: VectorRetrieverPort = Depends(get_vector_retriever),
    llm: LLMPort = Depends(get_llm),
    embedding: EmbeddingPort = Depends(get_embedding),
    event_bus: EventBusPort = Depends(get_event_bus),
) -> QueryService:
    """
    Get the query service.
    
    Args:
        vector_retriever (VectorRetrieverPort): Vector retriever implementation.
        llm (LLMPort): LLM implementation.
        embedding (EmbeddingPort): Embedding implementation.
        event_bus (EventBusPort): Event bus implementation.
    
    Returns:
        QueryService: Query service instance.
    """
    logger.debug("query_di :: Creating query service")
    return QueryService(
        vector_retriever_port=vector_retriever,
        llm_port=llm,
        embedding_port=embedding,
        rag_config=get_rag_config(),
        event_bus=event_bus,
    )


@lru_cache
def get_query_handler(
    query_service: QueryService = Depends(get_query_service),
    event_bus: EventBusPort = Depends(get_event_bus),
) -> QueryHandler:
    """
    Get the query handler.
    
    Args:
        query_service (QueryService): Query service.
        event_bus (EventBusPort): Event bus implementation.
    
    Returns:
        QueryHandler: Query handler instance.
    """
    logger.debug("query_di :: Creating query handler")
    return QueryHandler(query_service=query_service, event_bus=event_bus)
```

## Summary of Changes

1. Created an `EventBusPort` interface to define how the RAG component will publish events
2. Implemented a `RedisEventBusAdapter` that connects to the Redis event bus
3. Updated `QueryHandler` to publish events when:
   - A query is requested (`QueryRequestedEvent`)
   - A query is completed (`QueryCompletedEvent`)
4. Updated `QueryService` to publish events when:
   - Documents are retrieved (`DocumentsRetrievedEvent`)
5. Updated dependency injection to provide the event bus to the handlers and services

These changes enable event-based tracking of the RAG query process while maintaining the hexagonal architecture and domain-driven design principles.

nicolasRossard: j'ai créé des evenements mais maintenant j'en fais quoi ?

GitHub Copilot: # Next Steps for Your Event System Implementation

Now that you've created the events and set up the publishing side, you need to implement the tracking component that will consume these events. Here's what to do next:

## 1. Create the Tracking Component Structure

First, create the folder structure for the tracking component:

```bash
mkdir -p src/components/tracking/{application/{handlers,ports/{driven,driving}},domain/{entities,services,value_objects},infrastructure/{adapters/{driven,driving},api/v1,persistence/{models,repositories}}}
```

## 2. Define the Database Models

```python
"""Database model for query tracking."""

import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy import Column, DateTime, Float, Integer, JSON, String, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class QueryTrackingModel(Base):
    """SQLAlchemy model for tracking query events."""
    
    __tablename__ = "query_tracking"
    
    id = Column(String, primary_key=True)
    query_text = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(String, nullable=True)
    response_text = Column(String, nullable=True)
    processing_time = Column(Float, nullable=True)
    model_used = Column(String, nullable=True)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Relationship with retrieved documents
    retrieved_documents = relationship("DocumentRetrievalModel", back_populates="query")


class DocumentRetrievalModel(Base):
    """SQLAlchemy model for tracking document retrievals."""
    
    __tablename__ = "document_retrievals"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(String, ForeignKey("query_tracking.id"))
    document_id = Column(String, nullable=False)
    retrieval_score = Column(Float, nullable=True)
    position = Column(Integer, nullable=True)
    
    # Relationship with query
    query = relationship("QueryTrackingModel", back_populates="retrieved_documents")
```

## 3. Create Event Subscribers for Tracking

```python
"""Handler for processing query events and storing tracking data."""

import logging
from typing import Dict, Any

from src.components.tracking.application.ports.driven.query_repository_port import QueryRepositoryPort
from src.components.tracking.domain.entities.query_log import QueryLog
from src.components.tracking.domain.entities.document_retrieval_log import DocumentRetrievalLog
from src.shared.domain.events.query_events import QueryRequestedEvent, QueryCompletedEvent, DocumentsRetrievedEvent

logger = logging.getLogger(__name__)

class QueryTrackingHandler:
    """
    Handler for processing query events and storing tracking data.
    
    Subscribes to query events and stores them in the tracking database.
    """
    
    def __init__(self, query_repository: QueryRepositoryPort):
        """
        Initialize query tracking handler.
        
        Args:
            query_repository (QueryRepositoryPort): Repository for storing query tracking data.
        """
        self.query_repository = query_repository
        logger.info("query_tracking_handler :: Initialized QueryTrackingHandler")
    
    async def handle_query_requested(self, event_data: Dict[str, Any]) -> None:
        """
        Handle query requested event.
        
        Args:
            event_data (Dict[str, Any]): Event data containing query information.
        """
        logger.info("query_tracking_handler :: Handling query requested event")
        logger.debug(f"query_tracking_handler :: Event data: {event_data}")
        
        # Create query log entry
        query_log = QueryLog(
            id=event_data["payload"]["query_id"],
            query_text=event_data["payload"]["query_text"],
            user_id=event_data["payload"].get("user_id"),
            metadata=event_data["payload"].get("metadata", {})
        )
        
        # Store in repository
        await self.query_repository.create_query_log(query_log)
        logger.info(f"query_tracking_handler :: Stored query requested event for query ID: {query_log.id}")
    
    async def handle_documents_retrieved(self, event_data: Dict[str, Any]) -> None:
        """
        Handle documents retrieved event.
        
        Args:
            event_data (Dict[str, Any]): Event data containing retrieved documents information.
        """
        logger.info("query_tracking_handler :: Handling documents retrieved event")
        logger.debug(f"query_tracking_handler :: Event data: {event_data}")
        
        query_id = event_data["payload"]["query_id"]
        document_ids = event_data["payload"]["document_ids"]
        scores = event_data["payload"].get("scores", [None] * len(document_ids))
        
        # Create document retrieval logs
        retrieval_logs = []
        for i, (doc_id, score) in enumerate(zip(document_ids, scores)):
            retrieval_logs.append(
                DocumentRetrievalLog(
                    query_id=query_id,
                    document_id=doc_id,
                    retrieval_score=score,
                    position=i
                )
            )
        
        # Store in repository
        await self.query_repository.add_document_retrievals(retrieval_logs)
        logger.info(f"query_tracking_handler :: Stored {len(retrieval_logs)} document retrievals for query ID: {query_id}")
    
    async def handle_query_completed(self, event_data: Dict[str, Any]) -> None:
        """
        Handle query completed event.
        
        Args:
            event_data (Dict[str, Any]): Event data containing query completion information.
        """
        logger.info("query_tracking_handler :: Handling query completed event")
        logger.debug(f"query_tracking_handler :: Event data: {event_data}")
        
        query_id = event_data["payload"]["query_id"]
        
        # Update query log with completion data
        update_data = {
            "response_text": event_data["payload"]["response_text"],
            "processing_time": event_data["payload"]["processing_time"],
            "metadata": event_data["payload"].get("metadata", {})
        }
        
        # Extract additional metadata if available
        metadata = update_data["metadata"]
        if "model_used" in metadata:
            update_data["model_used"] = metadata["model_used"]
        if "input_tokens" in metadata:
            update_data["input_tokens"] = metadata["input_tokens"]
        if "output_tokens" in metadata:
            update_data["output_tokens"] = metadata["output_tokens"]
        
        # Update repository
        await self.query_repository.update_query_log(query_id, update_data)
        logger.info(f"query_tracking_handler :: Updated query log with completion data for query ID: {query_id}")
```

## 4. Connect Event Subscribers to the Event Bus

```python
"""Event bus subscriber for tracking component."""

import logging
from typing import Dict, Any, Optional

from src.components.tracking.application.handlers.query_tracking_handler import QueryTrackingHandler
from src.shared.infrastructure.event_bus.redis_event_bus import RedisEventBus
from src.shared.infrastructure.event_bus.interfaces import EventSubscriber, EventHandler

logger = logging.getLogger(__name__)

class TrackingEventSubscriber(EventSubscriber):
    """
    Event subscriber for the tracking component.
    
    Connects tracking handlers to the event bus.
    """
    
    def __init__(
        self,
        query_tracking_handler: QueryTrackingHandler,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        event_bus: Optional[RedisEventBus] = None
    ):
        """
        Initialize tracking event subscriber.
        
        Args:
            query_tracking_handler (QueryTrackingHandler): Handler for query events.
            redis_host (str): Redis server hostname. Defaults to "localhost".
            redis_port (int): Redis server port. Defaults to 6379.
            redis_db (int): Redis database number. Defaults to 0.
            event_bus (Optional[RedisEventBus]): Existing event bus instance to use.
                If None, a new instance will be created.
        """
        self.query_tracking_handler = query_tracking_handler
        self.event_bus = event_bus or RedisEventBus(
            redis_host=redis_host,
            redis_port=redis_port,
            redis_db=redis_db
        )
        logger.info("event_bus_subscriber :: Initialized TrackingEventSubscriber")
    
    def register_handler(self, event_type: str, handler: EventHandler) -> None:
        """
        Register a handler for a specific event type.
        
        Args:
            event_type (str): The type of event to handle.
            handler (EventHandler): The function to call when the event occurs.
        """
        logger.info(f"event_bus_subscriber :: Registering handler for event type: {event_type}")
        self.event_bus.subscribe(event_type, handler)
    
    def start_listening(self) -> None:
        """
        Start listening for events.
        
        Registers handlers for all relevant event types and starts the event bus.
        """
        logger.info("event_bus_subscriber :: Starting event listener")
        
        # Register handlers for query events
        self.register_handler("query.requested", self.query_tracking_handler.handle_query_requested)
        self.register_handler("documents.retrieved", self.query_tracking_handler.handle_documents_retrieved)
        self.register_handler("query.completed", self.query_tracking_handler.handle_query_completed)
        
        # Start the event bus
        self.event_bus.start()
        logger.info("event_bus_subscriber :: Event listener started successfully")
    
    def stop_listening(self) -> None:
        """
        Stop listening for events.
        
        Stops the event bus and cleans up resources.
        """
        logger.info("event_bus_subscriber :: Stopping event listener")
        self.event_bus.stop()
        logger.info("event_bus_subscriber :: Event listener stopped successfully")
```

## 5. Start the Event Subscriber in Your Application

Add this to your application startup code:

```python
# Add to existing imports
from src.components.tracking.infrastructure.adapters.driven.event_bus_subscriber import TrackingEventSubscriber
from src.components.tracking.application.handlers.query_tracking_handler import QueryTrackingHandler
from src.components.tracking.infrastructure.persistence.repositories.query_repository import SQLQueryRepository

# Initialize tracking components
query_repository = SQLQueryRepository()
query_tracking_handler = QueryTrackingHandler(query_repository)

# Start event subscriber
tracking_subscriber = TrackingEventSubscriber(
    query_tracking_handler=query_tracking_handler,
    redis_host="rag_event_broker"
)
tracking_subscriber.start_listening()

# Add to app shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    tracking_subscriber.stop_listening()
    # Other cleanup code...
```

## Next Steps

1. **Implement the repository**: Create `SQLQueryRepository` to handle database operations
2. **Set up database connection**: Configure SQLAlchemy for your database
3. **Create API endpoints**: Add endpoints to query the tracking data
4. **Add visualization**: Create a dashboard to visualize query statistics

This implementation follows hexagonal architecture principles by:
1. Keeping business logic in handlers and domain entities
2. Using ports and adapters to connect to external systems
3. Maintaining separation of concerns between tracking and RAG components
4. Using events for loose coupling between components