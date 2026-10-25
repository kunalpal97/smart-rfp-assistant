
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.permissions import require_user
from app.core.security import AuthenticatedUser
from app.schemas.user import CurrentUserResponse



router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=CurrentUserResponse,
)
def get_my_profile(
    current_user: Annotated[
        AuthenticatedUser,
        Depends(require_user),
    ],
) -> CurrentUserResponse:
    """Return the authenticated Microsoft Entra identity."""

    return CurrentUserResponse(
        tenant_id=current_user.tenant_id,
        object_id=current_user.object_id,
        roles=list(current_user.roles),
        scopes=list(current_user.scopes),
    )
