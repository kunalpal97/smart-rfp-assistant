
import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func, select

from app.storage.db_engine import get_db_session
from app.storage.models import AnswerHistory, Document


def get_knowledge_overview() -> dict:
    """Summarize the shared document registry."""

    with get_db_session() as session:
        row = session.execute(
            select(
                func.count(Document.document_id),
                func.coalesce(
                    func.sum(
                        case(
                            (Document.status == "ready", 1),
                            else_=0,
                        )
                    ),
                    0,
                ),
                func.coalesce(
                    func.sum(
                        case(
                            (Document.status == "processing", 1),
                            else_=0,
                        )
                    ),
                    0,
                ),
                func.coalesce(
                    func.sum(
                        case(
                            (Document.status == "failed", 1),
                            else_=0,
                        )
                    ),
                    0,
                ),
                func.coalesce(func.sum(Document.chunk_count), 0),
                func.max(Document.created_at),
            )
        ).one()

        (
            total,
            ready,
            processing,
            failed,
            chunks,
            latest_upload,
        ) = row

        attention_count = session.scalar(
            select(func.count(Document.document_id)).where(
                (Document.status == "failed")
                | (
                    (Document.status == "ready")
                    & (Document.chunk_count == 0)
                )
            )
        ) or 0

        return {
            "total_documents": int(total),
            "ready_documents": int(ready),
            "processing_documents": int(processing),
            "failed_documents": int(failed),
            "documents_needing_attention": int(attention_count),
            "total_chunks": int(chunks),
            "latest_upload_at": latest_upload,
        }


def get_answer_overview(
    *,
    tenant_id: str,
    user_id: str,
) -> dict:
    """Summarize only the signed-in user's answer history."""

    cutoff = (
        datetime.now(timezone.utc) - timedelta(days=7)
    ).isoformat()

    with get_db_session() as session:
        rows = session.execute(
            select(
                AnswerHistory.created_at,
                AnswerHistory.sources_json,
            ).where(
                AnswerHistory.tenant_id == tenant_id,
                AnswerHistory.user_id == user_id,
            )
        ).all()

    total = len(rows)
    recent = 0
    with_sources = 0

    for created_at, sources_json in rows:
        if created_at >= cutoff:
            recent += 1

        try:
            sources = json.loads(sources_json)
        except (TypeError, ValueError):
            sources = []

        if isinstance(sources, list) and len(sources) > 0:
            with_sources += 1

    without_sources = total - with_sources

    coverage = (
        round(with_sources / total * 100, 1)
        if total > 0
        else None
    )

    return {
        "total_answers": total,
        "answers_last_7_days": recent,
        "answers_with_sources": with_sources,
        "answers_without_sources": without_sources,
        "evidence_coverage_percent": coverage,
    }
