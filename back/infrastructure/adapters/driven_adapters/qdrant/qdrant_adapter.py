from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, SearchRequest

from domain.schema.document_chunk import DocumentChunk
from application.ports.server_side.vector_search_port import VectorSearchPort


class QdrantAdapter(VectorSearchPort):
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)

    def search(self, query: str) -> list[DocumentChunk]:
        # Assuming query embedding already exists or a mock here
        # query_vector = self.embed(query)
        # results = self.client.search(
        #     collection_name="documents",
        #     query_vector=query_vector,
        #     limit=5
        # )
        # return [DocumentChunk(id=point.id, text=point.payload['text'], score=point.score) for point in results]

        return [
            DocumentChunk(id="doc1", text="Le machine learning est une branche de l'intelligence artificielle.", score=0.95),
            DocumentChunk(id="doc2", text="Les réseaux de neurones convolutifs sont utilisés en vision par ordinateur.", score=0.89),
            DocumentChunk(id="doc3", text="L’apprentissage supervisé repose sur des données étiquetées.", score=0.87),
        ]
    
    def embed(self, query: str) -> list[float]:
        # Placeholder: use a real embedding model
        return [0.1] * 768