
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.permissions import require_user
from app.core.security import AuthenticatedUser
from app.schemas.dashboard import DashboardOverviewResponse
from app.storage.dashboard_repository import (
    get_answer_overview,
    get_knowledge_overview,
)


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/overview",
    response_model=DashboardOverviewResponse,
)
def get_dashboard_overview(
    current_user: Annotated[
        AuthenticatedUser,
        Depends(require_user),
    ],
) -> DashboardOverviewResponse:
    """Return knowledge and user-specific answer metrics."""

    return DashboardOverviewResponse(
        knowledge=get_knowledge_overview(),
        answers=get_answer_overview(
            tenant_id=current_user.tenant_id,
            user_id=current_user.object_id,
        ),
    )
