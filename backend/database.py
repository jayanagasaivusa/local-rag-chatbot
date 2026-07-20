"""
SQLAlchemy engine/session setup for the auth + chat-history database.
Connected to PostgreSQL/pgvector.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import DATABASE_URL

# PostgreSQL handles threading differently than SQLite; 
# no 'check_same_thread' required.
engine = create_engine(DATABASE_URL)
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
    """Creates all tables in PostgreSQL. Call once on startup."""
    import models 
    Base.metadata.create_all(bind=engine)