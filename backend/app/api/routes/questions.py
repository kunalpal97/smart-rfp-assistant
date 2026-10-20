
from fastapi import APIRouter

from app.schemas.question import QuestionRequest
from app.schemas.response import RFPAnswerResponse
from app.services.rag import answer_rfp_question

router = APIRouter(
    prefix="/api/questions",
    tags=["Questions"],
)


@router.post(
    "/ask",
    response_model=RFPAnswerResponse,
)
def ask_question(payload: QuestionRequest):
    return answer_rfp_question(
        payload.question,
        retrieval_mode="hybrid",
    )
