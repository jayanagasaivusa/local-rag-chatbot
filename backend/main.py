"""
FastAPI entrypoint for the local RAG chatbot backend.
Includes NVIDIA NeMo Guardrails for input/output data masking.
"""
import logging
import shutil
import uuid
import re
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

# NeMo Guardrails imports
from nemoguardrails import LLMRails, RailsConfig
from nemoguardrails.actions import action

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

# --- Guardrails Setup ---
rails_config = RailsConfig.from_path("./guardrails_config")
rails = LLMRails(rails_config)

@action(name="MaskSensitiveData")
def mask_sensitive_data(text: str):
    """Masks emails and phone numbers to protect PII."""
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL_MASKED]', text)
    text = re.sub(r'\d{3}-\d{3}-\d{4}', '[PHONE_MASKED]', text)
    return text

rails.register_action(mask_sensitive_data, name="MaskSensitiveData")
# ------------------------

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
    return {"documents": list_ingested_sources()}

@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    extension = Path(file.filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    safe_name = f"{uuid.uuid4().hex[:8]}_{Path(file.filename).name}"
    destination = DATA_DIR / safe_name

    try:
        with destination.open("wb") as out_file:
            shutil.copyfileobj(file.file, out_file)
    finally:
        file.file.close()

    documents = load_documents(destination)
    chunks_added = add_documents(documents)
    
    return UploadResponse(
        filename=file.filename,
        chunks_added=chunks_added,
        message=f"'{file.filename}' processed successfully.",
    )

def _get_or_create_session(db, user, session_id, first_message):
    if session_id:
        session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user.id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found.")
        return session
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
    # Mask input
    message = mask_sensitive_data(request.message.strip())
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    session = _get_or_create_session(db, current_user, request.session_id, message)
    db.add(Message(session_id=session.id, role=MessageRole.user, content=message))
    db.commit()

    try:
        # Generate answer
        result = answer_question(message)
        # Mask output
        result["response"] = mask_sensitive_data(result.get("response", ""))
    except Exception as exc:
        logger.exception("Failed to answer question")
        raise HTTPException(status_code=500, detail=str(exc))

    db.add(Message(session_id=session.id, role=MessageRole.assistant, content=result["response"]))
    db.commit()

    return ChatResponse(**result, session_id=session.id)