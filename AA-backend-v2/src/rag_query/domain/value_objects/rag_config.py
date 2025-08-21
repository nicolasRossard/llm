from pydantic import BaseModel, Field


class RAGConfig(BaseModel):
    """
    Represents the parameters for a Retrieval-Augmented Generation (RAG) operation.

    Attributes:
        top_k (int): Number of top documents to retrieve for RAG.
        system_prompt (str): System prompt used to guide the assistant's responses.
    """
    model_config = {
        "extra": "forbid",  # Disallow extra fields not defined in the model
        "allow_mutation": False   # Make the model immutable after creation
    }

    top_k: int = Field(5, description="Nombre de documents à récupérer pour le RAG.")
    system_prompt: str = Field(
        """You are a helpful assistant that answers questions based on the provided context.
If the answer is not in the context, say that you don't know instead of making up information.
Use the following retrieved documents to answer the user's question:
""",
        description="Prompt system used for guiding the assistant's responses."
    )