"""
Centralized configuration for the RAG backend.

All values can be overridden via environment variables (or a local .env
file, loaded automatically). Keeping this in one module means the rest of
the codebase never hardcodes paths or model names.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Where uploaded source files are stored.
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))

# Where Chroma persists its vector index on disk.
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", BASE_DIR / "chroma_db"))
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "rag_documents")

# Ollama connection + model names.
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
# Change the model name
OLLAMA_LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "gemma4:12b")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

# Text splitting.
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Retrieval.
RETRIEVER_TOP_K = int(os.getenv("RETRIEVER_TOP_K", "10"))

# CORS - the Vite dev server default origin.
FRONTEND_ORIGINS = os.getenv(
    "FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174"
).split(",")

DATA_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# Authentication Settings
JWT_SECRET_KEY = "super-secret-key-change-this-in-production"  
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # Tokens last for 7 days
# Database Settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:password123@postgres:5432/rag_db")