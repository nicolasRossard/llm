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