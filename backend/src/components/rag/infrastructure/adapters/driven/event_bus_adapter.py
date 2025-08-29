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