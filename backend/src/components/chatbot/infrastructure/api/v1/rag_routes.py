from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from src.components.chatbot.application.ports.driven.embedding_port import EmbeddingPort
from src.components.chatbot.application.ports.driving import ChatbotPort
from src.components.chatbot.application.use_case_handlers import ProcessChatQuery, ProcessDocumentIngestion

from src.components.chatbot.application.services import DocumentProcessingService, ChatbotService
from src.components.chatbot.domain.value_objects import Query, Response
from src.components.chatbot.domain.value_objects.input_document import DocumentType, InputDocument
from src.components.chatbot.infrastructure.api.v1.dto import response_to_dto
from src.components.chatbot.infrastructure.di import get_document_processing_service, get_chatbot_service, \
    get_embedding_port

rag_router = APIRouter(prefix="/chatbot", tags=["chatbot", "rag"])


@rag_router.post("/chat", response_model=dict)
async def process_chat_message(
    message: str,
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    """Process a chat message and return a response.
    
    This endpoint is the entry point for chat interactions, following the
    Hexagonal Architecture pattern. It:
    
    1. Receives the external request (HTTP)
    2. Transforms it into a domain Query object
    3. Passes it to the primary port (ChatbotPort)
    4. Returns the response
    
    The implementation details of how the message is processed are entirely
    hidden behind the ChatbotPort interface by using use case handler.
    """
    try:
        # Convert the message to a domain Query object
        query = Query(content=message)

        # Process the query through the port
        response = await ProcessChatQuery(chatbot_service=chatbot_service).process_chat_message(query)
        
        # Transform the domain response to an API response
        return response_to_dto(response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@rag_router.post("/upload/")
async def upload_file(
        file: UploadFile = File(...),
        doc_type: DocumentType = DocumentType.PDF,
        document_processing_service: DocumentProcessingService = Depends(get_document_processing_service)
):
    content = await file.read()
    input_doc = InputDocument(filename=file.filename, content=content, type=doc_type)
    # try:
    results = await ProcessDocumentIngestion(document_processing_service=document_processing_service).ingest_document(input_doc)
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))
    return results


@rag_router.post("/embed", response_model=dict)
async def create_text_embedding(
    text: str,
    embedding_service: EmbeddingPort = Depends(get_embedding_port)
):
    """Create an embedding for the given text.
    
    This endpoint takes a text input and returns its vector embedding
    using the configured embedding service.
    """
    try:
        embedding = await embedding_service.generate_embedding(text)
        return {"text": text, "embedding": embedding}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
