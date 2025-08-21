from pydantic import BaseModel, Field, ConfigDict


class VectorRepositoryConfig(BaseModel):
    """
    Configuration for the vector repository used in RAG (Retrieval-Augmented Generation).

    Attributes:
        embedding_model_name (str): Name of the embedding model to use.
        distance_type (str): Type of distance metric to use for similarity search.
        top_k (int): Number of documents to retrieve for RAG.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    embedding_model_name: str = Field(
        ...,
        description="embedding model name used to generate vector representations of documents."
    )
    distance_type: str = Field(
        ...,
        description="Distance type used for similarity search (e.g., 'cosine', 'euclidean')."
    )
    top_k: int = Field(5, description="number of documents to retrieve for RAG.")
