from typing import Union
from datetime import datetime

from src.components.chatbot.domain.value_objects import Response, RAGResponse


def response_to_dto(response: Union["Response", "RAGResponse"]) -> dict:
    """Converts a Response or RAGResponse object to a JSON-compatible dictionary.

    This function transforms Response or RAGResponse objects into dictionaries that can
    be safely serialized to JSON. It handles special conversions for RAGResponse sources
    and datetime objects.

    Args:
        response (Union["Response", "RAGResponse"]): The response object to convert.
            Can be either a Response or RAGResponse instance.

    Returns:
        dict: A JSON-compatible dictionary representation of the response.
            - For RAGResponse objects, includes properly formatted sources
            - Converts datetime objects to ISO format strings
    """
    dto = response.model_dump()

    if hasattr(response, "sources"):
        dto["sources"] = [
            {
                "id": str(source.id),  # UUID -> str
                "content": source.content,
                "metadata": source.metadata,
                "score": source.score,
            }
            for source in response.sources
        ]
    # Convert datetime to ISO string for JSON
    if isinstance(dto.get("generated_at"), datetime):
        dto["generated_at"] = dto["generated_at"].isoformat()
    return dto