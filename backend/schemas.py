"""
Pydantic request/response schemas for auth + chat-history endpoints.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from models import MessageRole

# --- Auth ------------------------------------------------------------------


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Chat sessions / messages ------------------------------------------------


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    role: MessageRole
    content: str
    created_at: datetime


class ChatSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    created_at: datetime


class ChatSessionCreate(BaseModel):
    title: str = "New Chat"
