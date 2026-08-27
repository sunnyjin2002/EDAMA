"""Database engine and session utilities."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.core.config import get_settings
from backend.db.base import Base

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_size=1,     # SQLite only allows one writer
    pool_timeout=30, # wait up to 30s for a connection
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def _slugify_title(title):
    import re
    if not title:
        return "article"
    value = title.lower().replace("'", "").replace("’", "")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "article"

def _source_prefix(source_type):
    if source_type in {"official_news", "community"}:
        return "news"
    if source_type == "community_goal":
        return "cg"
    return "manual"

def _build_article_slug(source_type, published_at, sequence):
    prefix = _source_prefix(source_type)
    if isinstance(published_at, str):
        day = published_at[:10]
        parts = day.split("-")
        if len(parts) == 3 and all(part.isdigit() for part in parts):
            year, month, day_num = [int(part) for part in parts]
        else:
            from datetime import datetime
            day_obj = datetime.utcnow().date()
            year, month, day_num = day_obj.year, day_obj.month, day_obj.day
    elif published_at:
        if hasattr(published_at, "year") and hasattr(published_at, "month") and hasattr(published_at, "day"):
            year, month, day_num = published_at.year, published_at.month, published_at.day
        else:
            from datetime import datetime
            day_obj = datetime.utcnow().date()
            year, month, day_num = day_obj.year, day_obj.month, day_obj.day
    else:
        from datetime import datetime
        day_obj = datetime.utcnow().date()
        year, month, day_num = day_obj.year, day_obj.month, day_obj.day
    return f"{prefix}-{year:04d}-{month:02d}-{day_num:02d}-{sequence}"

def _ensure_article_public_columns() -> None:
    """Add and backfill public article columns for existing SQLite databases.

    ``Base.metadata.create_all`` does not alter existing tables, so this
    small migration helper keeps older local app.db files compatible.
    """
    required = {
        "source_uid": "VARCHAR(255)",
        "legacy_source_uid": "VARCHAR(255)",
        "slug": "VARCHAR(255)",
        "article_header": "VARCHAR(500)",
    }

    with engine.begin() as conn:
        columns = {
            row[1]
            for row in conn.exec_driver_sql("PRAGMA table_info(articles)").fetchall()
        }
        for name, sql_type in required.items():
            if name not in columns:
                conn.exec_driver_sql(f"ALTER TABLE articles ADD COLUMN {name} {sql_type}")

        rows = conn.exec_driver_sql(
            "SELECT id, source_type, source_title, published_at_source "
            "FROM articles WHERE slug IS NULL OR article_header IS NULL"
        ).fetchall()

        sequence_by_key: dict[tuple[str, str], int] = {}
        for row in rows:
            article_id, source_type, source_title, published_at_source = row
            date_key = "legacy"
            if published_at_source:
                parsed = published_at_source[:10]
                date_key = parsed
            key = (source_type or "manual", date_key)
            sequence_by_key[key] = sequence_by_key.get(key, 0) + 1
            sequence = sequence_by_key[key]
            slug = _build_article_slug(source_type, published_at_source, sequence)
            header = _slugify_title(source_title)
            conn.exec_driver_sql(
                "UPDATE articles SET slug = ?, article_header = ? WHERE id = ?",
                (slug, header, article_id),
            )

def create_database_tables() -> None:
    """Create all registered tables for local development and smoke tests."""
    from backend.db import models  # noqa: F401
    from sqlalchemy import event

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record):
        """Enable WAL mode and set busy timeout for SQLite connections."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    _ensure_article_public_columns()


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for FastAPI dependencies."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
