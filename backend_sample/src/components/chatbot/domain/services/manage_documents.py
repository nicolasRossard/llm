from src.components.chatbot.application.ports.driven import EmbeddingPort, DocumentProcessingPort
from src.components.chatbot.domain.repositories import VectorRepository
from src.components.chatbot.domain.value_objects import InputDocument, DocumentRetrievalVector


class ManageDocuments:
    def __init__(self, vector_repository: VectorRepository, embedding_port: EmbeddingPort,
                 document_processing_port: DocumentProcessingPort):
        self.vector_repository = vector_repository
        self.embedding_port = embedding_port
        self.document_processing_port = document_processing_port

    def add_document(self, input_document: InputDocument) -> int:
        """Add a new document to the repository by processing, embedding, and storing it.

        This method takes an input document, processes it into chunks, generates embeddings
        for each chunk, and stores the resulting vectors in the vector repository for
        retrieval purposes.

        Args:
            input_document (InputDocument): The input document to be processed and added to the repository.

        Returns:
            int: The number of document chunks that were successfully added to the repository.

        Raises:
            TODO

        Example:
            >>> TODO
        """
        chunked_documents = self.document_processing_port.process_document(input_document)
        vectors = []

        for chunk in chunked_documents:
            # Generate embedding for each chunk
            embedding = self.embedding_port.generate_embedding(chunk.content)
            # Prepare the document for vector storage
            vector_data = {
                "id": chunk.id,
                "content": chunk.content,
                "embedding": embedding,
                "metadata": chunk.metadata
            }
            vectors.append(DocumentRetrievalVector(**vector_data))

        # Upsert the document into the vector repository
        vectors_stored_count = self.vector_repository.upsert(vectors)
        return vectors_stored_count  # TODO use status code instead of count
