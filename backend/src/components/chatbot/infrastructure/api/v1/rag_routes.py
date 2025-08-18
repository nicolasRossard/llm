from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from src.components.chatbot.application.ports.driving import ChatbotPort
from src.components.chatbot.application.use_cases import ProcessChatQuery
from src.components.chatbot.domain.value_objects import Query, Response
from src.components.chatbot.domain.value_objects.input_document import DocumentType, InputDocument
from src.components.chatbot.infrastructure.api.v1.dto import response_to_dto
from src.components.chatbot.infrastructure.di.container import get_chatbot_port


chatbot_rag_router = APIRouter(prefix="/chatbot", tags=["chatbot", "rag"])


@chatbot_rag_router.post("/chat", response_model=dict)
async def process_chat_message(
    message: str,
    chatbot_port: ChatbotPort = Depends(get_chatbot_port)
):
    """Process a chat message and return a response.
    
    This endpoint is the entry point for chat interactions, following the
    Hexagonal Architecture pattern. It:
    
    1. Receives the external request (HTTP)
    2. Transforms it into a domain Query object
    3. Passes it to the primary port (ChatbotPort)
    4. Returns the response
    
    The implementation details of how the message is processed are entirely
    hidden behind the ChatbotPort interface.
    """
    try:
        # Convert the message to a domain Query object
        query = Query(content=message)

        # Process the query through the port
        response = await ProcessChatQuery(chatbot_port=chatbot_port).execute(query)
        
        # Transform the domain response to an API response
        return response_to_dto(response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chatbot_rag_router.post("/upload/")
async def upload_file(file: UploadFile = File(...), doc_type: DocumentType = DocumentType.PDF):
    # Lire le contenu du fichier
    content = await file.read()

    # Créer ton modèle InputDocument
    input_doc = InputDocument(content=content, type=doc_type)

    return {
        "filename": file.filename,
        "size": len(input_doc.content),
        "type": input_doc.type,
    }