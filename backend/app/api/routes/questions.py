
"""RFP question answering endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.permissions import require_user
from app.core.security import AuthenticatedUser

from app.schemas.question import QuestionRequest
from app.schemas.response import RFPAnswerResponse

from app.services.rag import answer_rfp_question
from app.services.history_service import save_answer_history


router = APIRouter(
    prefix="/api/questions",
    tags=["Questions"],
)


@router.post(
    "/ask",
    response_model=RFPAnswerResponse,
)
def ask_question(
    payload: QuestionRequest,
    current_user: Annotated[
        AuthenticatedUser,
        Depends(require_user),
    ],
):
    """Generate an RFP answer and save it to user history."""

    # Step 1: Generate the answer using the existing RAG pipeline.
    rag_result = answer_rfp_question(
        payload.question,
        retrieval_mode="hybrid",
    )

    # Step 2: Validate and normalize the RAG response.
    answer_response = RFPAnswerResponse.model_validate(
        rag_result
    )

    # Step 3: Save the generated answer under the signed-in user.
    save_answer_history(
        tenant_id=current_user.tenant_id,
        user_id=current_user.object_id,
        question=payload.question,
        answer=answer_response.answer,
        sources=[
            source.model_dump(mode="json")
            for source in answer_response.sources
        ],
    )

    # Step 4: Return the original response format to React.
    return answer_response
