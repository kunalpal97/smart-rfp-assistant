
from fastapi import APIRouter, HTTPException

from app.schemas.question import QuestionRequest
from app.services.rag import answer_rfp_question


router = APIRouter(prefix="/api/questions", tags=["Questions"])


@router.post("/ask")
def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(
            status_code=422,
            detail="Question cannot be blank.",
        )

    return answer_rfp_question(request.question)
