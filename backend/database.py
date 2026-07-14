"""
SQLAlchemy engine/session setup for the auth + chat-history database.

Uses a local SQLite file (see `DATABASE_URL` in config.py). Import
`get_db` as a FastAPI dependency wherever a request needs DB access.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import DATABASE_URL

# `check_same_thread` is required for SQLite when the same connection may be
# touched by different request threads under FastAPI's threadpool.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Creates all tables that don't exist yet. Call once on startup."""
    import models  # noqa: F401  (ensures models are registered on Base)

    Base.metadata.create_all(bind=engine)
