import logging
from typing import List, Any, Coroutine

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile

from src.components.rag.application.handlers.query_handler import QueryHandler
from src.components.rag.application.ports.driven import TextChunkingPort
from src.components.rag.domain.value_objects import Query, RAGResponse, InputDocument, DocumentRetrieval, \
    DocumentRetrievalVector, StoreDocumentResult, Embedding
from src.components.rag.domain.value_objects.extracted_content import ExtractedContent
from src.components.rag.infrastructure.adapters.driven import DoclingTextExtractionAdapter, DoclingTextChunkingAdapter, \
    LiteLLMEmbeddingAdapter
from src.components.rag.infrastructure.api.di.query_di import get_query_handler
from src.components.rag.infrastructure.api.v1.dto import rag_response_to_dto
from src.components.rag.infrastructure.persistence import QdrantVectorStoreAdapter

# Create a router for RAG endpoints
rag_router = APIRouter(prefix="/rag", tags=["rag"])

# Setup logging
logger = logging.getLogger(__name__)


@rag_router.post("/chat", response_model=RAGResponse)
async def chat(request: str, handler: QueryHandler = Depends(get_query_handler)) -> dict:
    """
    Process a user query through the RAG system.
    
    Args:
        request: The query request containing the user's question.
        handler: The query handler dependency.
    
    Returns:
        RAGResponse: Response containing the generated answer and source documents.
    
    Raises:
        HTTPException: If an error occurs during query processing.
    """
    logger.info("chat :: Processing new chat request")

    # Create domain query object from request
    query = Query(content=request)

    # Process the query
    response = await handler.query(query)

    logger.info("chat :: Query processed successfully")
    return await rag_response_to_dto(response)


@rag_router.post("/admin/extract_text", response_model=ExtractedContent)
async def extract_text(file: UploadFile = File(...)) -> ExtractedContent:
    """
    Extract text content from a document at the given URL.

    Args:
        file: The uploaded file from which to extract text.

    Returns:
        ExtractedContent: Response containing the extracted text content.

    Raises:
        HTTPException: If an error occurs during text extraction.
    """
    logger.info("extract_text :: Processing new text extraction request")
    contents = b""
    while chunk := await file.read(1024):  # read 1 KB at a time
        contents += chunk
    document: InputDocument = InputDocument(content=contents, filename=file.filename, type=file.content_type)

    docling_text_extraction_adapter = DoclingTextExtractionAdapter()
    try:
        result: ExtractedContent = await docling_text_extraction_adapter.extract_text(document)

        logger.info("extract_text :: Text extraction completed successfully")
        return result

    except ValueError as e:
        logger.error(f"extract_text :: Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"extract_text :: Error extracting text: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while extracting text from the document")


@rag_router.post("/admin/chunk_text", response_model=List[DocumentRetrieval])
async def chunk_text(content: ExtractedContent) -> list[DocumentRetrieval]:
    """
    Chunk the provided text into smaller segments.

    Args:
        content: The text content to be chunked.

    Returns:
        List[DocumentRetrieval]: List of chunked text segments.

    Raises:
        HTTPException: If an error occurs during text chunking.
    """
    logger.info("chunk_text :: Processing new text chunking request")

    try:
        docling_text_chunking_adapter: TextChunkingPort = DoclingTextChunkingAdapter()
        result: List[DocumentRetrieval] = await docling_text_chunking_adapter.chunk_text(content)

        logger.info("chunk_text :: Text chunking completed successfully")
        logger.debug(f"chunk_text :: Generated {len(result)} chunks")
        return result

    except ValueError as e:
        logger.error(f"chunk_text :: Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"chunk_text :: Error during text chunking: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while chunking the text content")


@rag_router.post("/admin/chunk_embed", response_model=List[DocumentRetrievalVector])
async def embed_chunk(documents: list[DocumentRetrieval]) -> list[DocumentRetrievalVector]:
    embedding = LiteLLMEmbeddingAdapter()
    docs = []
    for doc in documents:
        vector: Embedding = await embedding.embed_text(doc.content)
        doc_vector: DocumentRetrievalVector = DocumentRetrievalVector(**doc.model_dump(), vector=vector.vector)
        docs.append(doc_vector)
    return docs


@rag_router.post("/admin/upsert_documents", response_model=StoreDocumentResult)
async def upsert_documents(documents: List[DocumentRetrievalVector]):
    vector_store = QdrantVectorStoreAdapter()
    # try:
    result: StoreDocumentResult = await vector_store.upsert(documents)
    return result
    # except Exception as e:
    #     logger.error(f"upsert_documents :: Error during upsert operation: {str(e)}")
    #     raise HTTPException(status_code=500, detail="An error occurred while upserting documents")
