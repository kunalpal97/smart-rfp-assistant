
"""SQLAlchemy repository for user-specific RAG answer history.

Supports SQLite locally and PostgreSQL after migration.
Every history operation is scoped to tenant_id and user_id.
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import func, select, delete, case, or_

from app.storage.db_engine import engine, get_db_session
from app.storage.models import AnswerHistory

logger = logging.getLogger(__name__)


def _utc_now() -> str:
    """Return a UTC timestamp compatible with existing records."""
    return datetime.now(timezone.utc).isoformat()


def _serialize_history(record: AnswerHistory) -> dict:
    """Convert a history ORM object to the existing response format."""

    return {
        "id": record.id,
        "tenant_id": record.tenant_id,
        "user_id": record.user_id,
        "question": record.question,
        "answer": record.answer,
        "sources": json.loads(record.sources_json),
        "created_at": record.created_at,
    }


def initialize_history_table() -> None:
    """Create the history table if it does not exist.

    Alembic will manage schema changes after migration setup.
    """

    AnswerHistory.__table__.create(
        bind=engine,
        checkfirst=True,
    )


def create_history_entry(
    *,
    tenant_id: str,
    user_id: str,
    question: str,
    answer: str,
    sources: list[dict],
) -> dict:
    """Save a generated answer for an authenticated user."""

    history_id = str(uuid4())
    created_at = _utc_now()

    entry = AnswerHistory(
        id=history_id,
        tenant_id=tenant_id,
        user_id=user_id,
        question=question,
        answer=answer,
        sources_json=json.dumps(sources),
        created_at=created_at,
    )

    with get_db_session() as session:
        session.add(entry)
        session.flush()

    return {
        "id": history_id,
        "tenant_id": tenant_id,
        "user_id": user_id,
        "question": question,
        "answer": answer,
        "sources": sources,
        "created_at": created_at,
    }


def list_user_history(
    *,
    tenant_id: str,
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    search: str = "",
    source_filter: str = "all",
    sort: str = "newest",
) -> dict:
    """Return paginated, searchable history for one user.

    The items and total count use identical filters.
    """

    if not tenant_id or not user_id:
        raise ValueError(
            "Authenticated user identity is required."
        )

    if not 1 <= limit <= 100:
        raise ValueError(
            "Limit must be between 1 and 100."
        )

    if offset < 0:
        raise ValueError(
            "Offset cannot be negative."
        )

    if source_filter not in {
        "all",
        "with_sources",
        "without_sources",
    }:
        raise ValueError(
            "Invalid source filter."
        )

    if sort not in {"newest", "oldest"}:
        raise ValueError(
            "Invalid sort order."
        )

    search = search.strip()

    if len(search) > 200:
        raise ValueError(
            "Search must not exceed 200 characters."
        )

    conditions = [
        AnswerHistory.tenant_id == tenant_id,
        AnswerHistory.user_id == user_id,
    ]

    if search:
        # Escape SQL LIKE wildcard characters so user input
        # is treated as literal text, not a wildcard pattern.
        escaped_search = (
            search
            .replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
        )

        pattern = f"%{escaped_search}%"

        conditions.append(
            or_(
                AnswerHistory.question.ilike(
                    pattern,
                    escape="\\",
                ),
                AnswerHistory.answer.ilike(
                    pattern,
                    escape="\\",
                ),
            )
        )

    # sources_json is serialized with json.dumps().
    # Empty citations are stored as "[]".
    has_no_sources = (
        func.trim(AnswerHistory.sources_json) == "[]"
    )

    if source_filter == "with_sources":
        conditions.append(~has_no_sources)

    elif source_filter == "without_sources":
        conditions.append(has_no_sources)

    if sort == "oldest":
        ordering = (
            AnswerHistory.created_at.asc(),
            AnswerHistory.id.asc(),
        )
    else:
        ordering = (
            AnswerHistory.created_at.desc(),
            AnswerHistory.id.desc(),
        )

    with get_db_session() as session:
        total = session.scalar(
            select(func.count(AnswerHistory.id))
            .where(*conditions)
        ) or 0

        records = session.scalars(
            select(AnswerHistory)
            .where(*conditions)
            .order_by(*ordering)
            .limit(limit)
            .offset(offset)
        ).all()

        return {
            "items": [
                _serialize_history(record)
                for record in records
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }


def get_history_entry(
    *,
    history_id: str,
    tenant_id: str,
    user_id: str,
) -> dict | None:
    """Retrieve a history entry belonging to the authenticated user."""

    with get_db_session() as session:
        record = session.scalar(
            select(AnswerHistory).where(
                AnswerHistory.id == history_id,
                AnswerHistory.tenant_id == tenant_id,
                AnswerHistory.user_id == user_id,
            )
        )

        return (
            _serialize_history(record)
            if record is not None
            else None
        )


def delete_history_entry(
    *,
    history_id: str,
    tenant_id: str,
    user_id: str,
) -> bool:
    """Delete a history entry only if it belongs to the user."""

    with get_db_session() as session:
        result = session.execute(
            delete(AnswerHistory).where(
                AnswerHistory.id == history_id,
                AnswerHistory.tenant_id == tenant_id,
                AnswerHistory.user_id == user_id,
            )
        )

        return result.rowcount > 0


def get_user_history_stats(
    *,
    tenant_id: str,
    user_id: str,
) -> dict:
    """Return answer statistics for one authenticated user."""

    seven_days_ago = (
        datetime.now(timezone.utc) - timedelta(days=7)
    ).isoformat()

    with get_db_session() as session:
        total_answers, answers_last_7_days = session.execute(
            select(
                func.count(AnswerHistory.id),
                func.count(
                    case(
                        (
                            AnswerHistory.created_at >= seven_days_ago,
                            1,
                        )
                    )
                ),
            ).where(
                AnswerHistory.tenant_id == tenant_id,
                AnswerHistory.user_id == user_id,
            )
        ).one()

        return {
            "total_answers": total_answers,
            "answers_last_7_days": answers_last_7_days,
        }
