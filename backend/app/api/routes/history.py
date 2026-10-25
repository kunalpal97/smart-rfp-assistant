
"""Authenticated answer history endpoints."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.permissions import require_user
from app.core.security import AuthenticatedUser
from app.schemas.history import (
    HistoryDeleteResponse,
    HistoryEntry,
    HistoryListResponse,
    
    
)
from app.services.history_service import (
    get_user_answer_history,
    get_user_history_detail,
    remove_user_history,
    get_answer_history_stats,
)


router = APIRouter(
    prefix="/api/history",
    tags=["History"],
)


@router.get("", response_model=HistoryListResponse)
def list_history(
    current_user: Annotated[
        AuthenticatedUser,
        Depends(require_user),
    ],
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    search: str = Query(default="", max_length=200),
    source_filter: Literal[
        "all",
        "with_sources",
        "without_sources",
    ] = Query(default="all"),
    sort: Literal[
        "newest",
        "oldest",
    ] = Query(default="newest"),
):
    """List searchable answers belonging to the signed-in user."""

    
    return get_user_answer_history(
        tenant_id=current_user.tenant_id,
        user_id=current_user.object_id,
        limit=limit,
        offset=offset,
        search=search,
        source_filter=source_filter,
        sort=sort,
    )


@router.get("/stats")
def get_history_stats(
    current_user: Annotated[
        AuthenticatedUser,
        Depends(require_user),
    ],
):
    """Return statistics for the signed-in user's history."""

    return get_answer_history_stats(
        tenant_id=current_user.tenant_id,
        user_id=current_user.object_id,
    )

@router.get("/{history_id}", response_model=HistoryEntry)
def get_history(
    history_id: str,
    current_user: Annotated[
        AuthenticatedUser,
        Depends(require_user),
    ],
):
    """Retrieve one of the signed-in user's answers."""

    entry = get_user_history_detail(
        history_id=history_id,
        tenant_id=current_user.tenant_id,
        user_id=current_user.object_id,
    )

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="History entry not found.",
        )

    return entry


@router.delete(
    "/{history_id}",
    response_model=HistoryDeleteResponse,
)
def delete_history(
    history_id: str,
    current_user: Annotated[
        AuthenticatedUser,
        Depends(require_user),
    ],
):
    """Delete one of the signed-in user's answers."""

    deleted = remove_user_history(
        history_id=history_id,
        tenant_id=current_user.tenant_id,
        user_id=current_user.object_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="History entry not found.",
        )

    return {"message": "History entry deleted successfully."}


