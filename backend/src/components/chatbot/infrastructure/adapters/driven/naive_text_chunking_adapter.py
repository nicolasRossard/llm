import uuid

from src.components.chatbot.application.ports.driven import TextChunkingPort
from src.components.chatbot.domain.value_objects import DocumentRetrieval


class NaiveTextChunkingAdapter(TextChunkingPort):
    """
    A naive text chunking adapter that splits text into chunks of a specified size.
    This is a simple implementation that does not consider context or semantics.
    """

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, metadata: dict) -> list[DocumentRetrieval]:
        """
        Splits the input text into chunks of the specified size with overlap.

        Args:
            text (str): The input text to be chunked.
            metadata (dict): Metadata to associate with each chunk.

        Returns:
            list[DocumentRetrieval]: A list of DocumentRetrieval objects containing 
                text chunks with unique IDs and metadata.
        """
        chunks = []
        step = self.chunk_size - self.overlap
        chunk_index = 0
        
        for i in range(0, len(text), step):
            chunk_text = text[i:i + self.chunk_size]
            if chunk_text.strip():  # Only add non-empty chunks
                # Create enhanced metadata with chunk information
                enhanced_metadata = metadata.copy()
                enhanced_metadata.update({
                    'chunk_index': chunk_index,
                    'start_position': i,
                    'end_position': min(i + self.chunk_size, len(text)),
                    'chunk_length': len(chunk_text)
                })
                
                chunks.append(
                    DocumentRetrieval(
                        id=uuid.uuid4(),
                        content=chunk_text,
                        metadata=enhanced_metadata
                    )
                )
                chunk_index += 1
        
        return chunks