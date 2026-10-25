"""SQLAlchemy database engine and session utilities."""

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.storage.database import get_database_path


def build_database_url() -> str:
    """Build the database URL for the selected provider."""

    settings = get_settings()

    if settings.database_provider == "sqlite":
        db_path = get_database_path()
        db_path.parent.mkdir(parents=True, exist_ok=True)

        return f"sqlite:///{db_path}"

    if settings.database_provider == "postgresql":
        if not settings.database_url:
            raise ValueError(
                "DATABASE_URL is required when "
                "DATABASE_PROVIDER=postgresql"
            )

        if not settings.database_url.startswith(
            "postgresql+psycopg://"
        ):
            raise ValueError(
                "PostgreSQL URL must use the "
                "postgresql+psycopg:// driver."
            )

        return settings.database_url

    raise ValueError(
        f"Unsupported database provider: "
        f"{settings.database_provider}"
    )


def create_database_engine() -> Engine:
    """Create a SQLAlchemy engine for SQLite or PostgreSQL."""

    settings = get_settings()
    database_url = build_database_url()

    engine_options = {
        "pool_pre_ping": True,
    }

    if settings.database_provider == "sqlite":
        engine_options["connect_args"] = {
            "timeout": 30,
        }
    else:
        engine_options.update({
            "pool_size": 5,
            "max_overflow": 10,
            "pool_timeout": 30,
            "pool_recycle": 1800,
        })

    return create_engine(
        database_url,
        **engine_options,
    )


engine = create_database_engine()

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


@contextmanager
def get_db_session() -> Iterator[Session]:
    """Provide a transactional database session."""

    session = SessionLocal()

    try:
        yield session
        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()