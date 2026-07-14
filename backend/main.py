"""
FastAPI entrypoint for the local RAG chatbot backend.

Replaces the original Jupyter notebook workflow with two HTTP endpoints:
  - POST /upload : ingest a document (PDF/Excel/HTML) into Chroma
  - POST /chat   : ask a question, answered via retrieval + local Ollama LLM

Run with:  uvicorn main:app --reload --port 8000
"""
import logging
import shutil
import uuid
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import get_current_user
from config import DATA_DIR, FRONTEND_ORIGINS, OLLAMA_LLM_MODEL
from database import get_db, init_db
from models import ChatSession, Message, MessageRole, User
from rag.chain import answer_question
from rag.loaders import UnsupportedFileTypeError, SUPPORTED_EXTENSIONS, load_documents
from rag.vectorstore import add_documents, list_ingested_sources
from routers import auth_routes, sessions as sessions_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rag-backend")

app = FastAPI(title="Local RAG Chatbot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(sessions_router.router)


@app.on_event("startup")
def on_startup():
    init_db()


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    sources: list[str]
    session_id: str


class UploadResponse(BaseModel):
    filename: str
    chunks_added: int
    message: str


class DocumentsResponse(BaseModel):
    documents: list[str]


@app.get("/health")
def health_check():
    return {"status": "ok", "llm_model": OLLAMA_LLM_MODEL}


@app.get("/documents", response_model=DocumentsResponse)
def get_documents():
    """Lists the distinct source filenames currently ingested into Chroma."""
    return {"documents": list_ingested_sources()}


@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Saves an uploaded file to disk, then loads/splits/embeds it into Chroma."""
    extension = Path(file.filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type '{extension}'. Supported types: "
                f"{', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            ),
        )

    # Prefix with a short uuid to avoid clobbering same-named uploads.
    safe_name = f"{uuid.uuid4().hex[:8]}_{Path(file.filename).name}"
    destination = DATA_DIR / safe_name

    try:
        with destination.open("wb") as out_file:
            shutil.copyfileobj(file.file, out_file)
    finally:
        file.file.close()

    try:
        documents = load_documents(destination)
        for doc in documents:
            doc.metadata.setdefault("source", file.filename)
            doc.metadata["source"] = file.filename  # keep the original, user-facing name
        chunks_added = add_documents(documents)
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Failed to process uploaded file %s", file.filename)
        raise HTTPException(
            status_code=500, detail=f"Failed to process file: {exc}"
        ) from exc

    return UploadResponse(
        filename=file.filename,
        chunks_added=chunks_added,
        message=f"'{file.filename}' processed and added to the knowledge base.",
    )


def _get_or_create_session(db: Session, user: User, session_id: str | None, first_message: str) -> ChatSession:
    if session_id:
        session = (
            db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.user_id == user.id)
            .first()
        )
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found.")
        return session

    # No session_id supplied -> start a new thread, titled from the first message.
    title = first_message[:60] + ("..." if len(first_message) > 60 else "")
    session = ChatSession(user_id=user.id, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Runs retrieval against Chroma, generates an answer via Ollama, and
    persists both the user's prompt and the AI's response to the DB."""
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    session = _get_or_create_session(db, current_user, request.session_id, message)

    db.add(Message(session_id=session.id, role=MessageRole.user, content=message))
    db.commit()

    try:
        result = answer_question(message)
    except Exception as exc:
        logger.exception("Failed to answer question")
        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to generate a response: {exc}. "
                "Is Ollama running locally with the configured model pulled?"
            ),
        ) from exc

    db.add(Message(session_id=session.id, role=MessageRole.assistant, content=result.get("response", "")))
    db.commit()

    return ChatResponse(**result, session_id=session.id)