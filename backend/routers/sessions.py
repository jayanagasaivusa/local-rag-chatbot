"""
GET /sessions and GET /sessions/{session_id}/messages.

All routes require a valid JWT and only ever operate on sessions owned by
the authenticated user.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import ChatSession, Message, User
from schemas import ChatSessionOut, MessageOut

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _get_owned_session(db: Session, session_id: str, user: User) -> ChatSession:
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    return session


@router.get("", response_model=list[ChatSessionOut])
def list_sessions(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Returns the current user's chat threads, most recent first."""
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )


@router.get("/{session_id}/messages", response_model=list[MessageOut])
def get_session_messages(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the full message history for one of the user's sessions."""
    session = _get_owned_session(db, session_id, current_user)
    return session.messages


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = _get_owned_session(db, session_id, current_user)
    db.delete(session)
    db.commit()
