
"""Business logic for RFP answer history."""

from app.storage.history_repository import (
    create_history_entry,
    delete_history_entry,
    get_history_entry,
    list_user_history,
    
)
from app.storage.history_repository import get_user_history_stats


def save_answer_history(
    *,
    tenant_id: str,
    user_id: str,
    question: str,
    answer: str,
    sources: list[dict],
) -> dict:
    """Persist a successfully generated RFP answer."""

    if not tenant_id or not user_id:
        raise ValueError("Authenticated user identity is required.")

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if not answer.strip():
        raise ValueError("Answer cannot be empty.")

    return create_history_entry(
        tenant_id=tenant_id,
        user_id=user_id,
        question=question.strip(),
        answer=answer,
        sources=sources,
    )


def get_user_answer_history(
    *,
    tenant_id: str,
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    search: str = "",
    source_filter: str = "all",
    sort: str = "newest",
) -> dict:
    """Return paginated history for the signed-in user."""

    return list_user_history(
        tenant_id=tenant_id,
        user_id=user_id,
        limit=limit,
        offset=offset,
        search=search,
        source_filter=source_filter,
        sort=sort,
    )


def get_user_history_detail(
    *,
    history_id: str,
    tenant_id: str,
    user_id: str,
) -> dict | None:
    """Return a history entry if it belongs to the user."""

    return get_history_entry(
        history_id=history_id,
        tenant_id=tenant_id,
        user_id=user_id,
    )


def remove_user_history(
    *,
    history_id: str,
    tenant_id: str,
    user_id: str,
) -> bool:
    """Delete a history entry belonging to the user."""

    return delete_history_entry(
        history_id=history_id,
        tenant_id=tenant_id,
        user_id=user_id,
    )



def get_answer_history_stats(
    *,
    tenant_id: str,
    user_id: str,
) -> dict:
    """Get dashboard statistics for the signed-in user."""

    if not tenant_id or not user_id:
        raise ValueError(
            "Authenticated user identity is required."
        )

    return get_user_history_stats(
        tenant_id=tenant_id,
        user_id=user_id,
    )