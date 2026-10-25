"""initial database schema

Revision ID: afe5d963d83c
Revises: 
Create Date: 2026-10-23 17:46:46.940954

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afe5d963d83c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Create the initial Smart RFP database schema."""

    op.create_table(
        "documents",
        sa.Column("document_id", sa.Text(), primary_key=True),
        sa.Column("filename", sa.Text(), nullable=False),
        sa.Column("stored_filename", sa.Text(), nullable=False),
        sa.Column("file_hash", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column(
            "chunk_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.Text(), nullable=False),
        sa.Column(
            "storage_provider",
            sa.Text(),
            nullable=False,
            server_default="local",
        ),
        sa.UniqueConstraint("file_hash"),
        sa.CheckConstraint(
            "status IN ('processing', 'ready', 'failed')",
            name="ck_documents_status",
        ),
    )

    op.create_table(
        "answer_history",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("tenant_id", sa.Text(), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column(
            "sources_json",
            sa.Text(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("created_at", sa.Text(), nullable=False),
    )

    op.create_index(
        "idx_history_user_created",
        "answer_history",
        ["tenant_id", "user_id", sa.text("created_at DESC")],
        unique=False,
    )


def downgrade() -> None:
    """Remove the initial database schema."""

    op.drop_index(
        "idx_history_user_created",
        table_name="answer_history",
    )

    op.drop_table("answer_history")
    op.drop_table("documents")

