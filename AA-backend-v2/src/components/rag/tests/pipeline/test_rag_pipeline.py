import pytest
import uuid
from src.components.rag.domain.value_objects import DocumentRetrieval, RAGResponse, Response
from src.components.rag.domain.pipeline import RAGPipeline


@pytest.mark.asyncio
async def test_generate_response_rag_pipeline():
    # Arrange
    rag_pipeline = RAGPipeline()

    # Créer un objet Response simulé
    llm_output = Response(
        content="This is a test LLM output",
        model_used="test-model",
        processing_time_ms=123,
        input_tokens=50,
        output_tokens=25
    )

    # Créer quelques documents simulés
    doc1 = DocumentRetrieval(
        id=uuid.uuid4(),
        content="Document 1 content",
        metadata={"source": "source1"},
        score=0.9
    )
    doc2 = DocumentRetrieval(
        id=uuid.uuid4(),
        content="Document 2 content",
        metadata={"source": "source2"},
        score=0.8
    )
    retrieved_chunks = [doc1, doc2]

    # Act
    rag_response = await rag_pipeline.generate_response(user_query="fake question", llm_output=llm_output, retrieved_chunks=retrieved_chunks)

    # Assert
    assert isinstance(rag_response, RAGResponse)
    assert rag_response.content == llm_output.content
    assert rag_response.model_used == llm_output.model_used
    assert rag_response.processing_time_ms == llm_output.processing_time_ms
    assert rag_response.input_tokens == llm_output.input_tokens
    assert rag_response.output_tokens == llm_output.output_tokens
    assert rag_response.sources == retrieved_chunks
    assert len(rag_response.sources) == 2
    assert rag_response.sources[0].content == "Document 1 content"
    assert rag_response.sources[1].metadata["source"] == "source2"
