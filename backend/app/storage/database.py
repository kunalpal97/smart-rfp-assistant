
"""Shared SQLite database connection utilities."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.core.config import get_settings


def get_database_path() -> Path:
    """Return the application's SQLite database path."""

    return get_settings().chroma_dir.parent / "documents.db"


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Provide a SQLite connection with transaction handling."""

    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        db_path,
        timeout=30,
    )

    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
