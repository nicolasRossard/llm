from fastapi import APIRouter
from domain.schema.query import Query
from domain.schema.answer import Answer
from application.ports.user_side.usecase_handler.answer_question_handler import AnswerQuestionHandler
from domain.service.rag_service import RagService
from infrastructure.adapters.server_side.lite_llm.lite_llm_client_adapter import LiteLlmClientAdapter
from infrastructure.adapters.server_side.llm_ollama.ollama_llm_client_adapter import OllamaLlmClientAdapter
from infrastructure.adapters.server_side.qdrant.qdrant_adapter import QdrantAdapter
from infrastructure.adapters.user_side.rest.dto import AnswerDTO, QuestionDTO
from infrastructure.adapters.user_side.rest.mapper import to_domain, to_dto

rag_router = APIRouter(prefix="/rag", tags=["RAG"])

# Dependency injection
vector_adapter = QdrantAdapter()
llm_rag_adapter = OllamaLlmClientAdapter()
rag_service = RagService(vector_adapter, llm_rag_adapter)
use_case_handler = AnswerQuestionHandler(rag_service)
litellm_adapter = LiteLlmClientAdapter()
litellm_rag_service = RagService(vector_adapter, litellm_adapter)
litellm_use_case_handler = AnswerQuestionHandler(litellm_rag_service)


@rag_router.post("/litellm/answer", response_model=AnswerDTO)
def answer_question(request_dto: QuestionDTO):
    # Mapping DTO vers modèle du domaine
    query = to_domain(request_dto)

    # Exécution du cas d’usage
    generated_answer = use_case_handler.execute(query)

    return to_dto(generated_answer)

@rag_router.post("/ollama/answer", response_model=AnswerDTO)
def answer_question(request_dto: QuestionDTO):
    # Mapping DTO vers modèle du domaine
    query = to_domain(request_dto)

    # Exécution du cas d’usage
    answer = litellm_use_case_handler.execute(query)

    # Mapping modèle du domaine → DTO de sortie
    return to_dto(answer)
