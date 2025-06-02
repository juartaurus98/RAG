"""
Schema cho API endpoints.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class MessageRequest(BaseModel):
    """Schema cho request tạo message."""
    question: str
    file_path: Optional[str] = None
    session_id: Optional[str] = None


class MessageResponse(BaseModel):
    """Schema cho response message."""
    answer: str
    context: Optional[str] = None
    session_id: Optional[str] = None


class ChatMessage(BaseModel):
    """Schema cho một tin nhắn trong chat history."""
    role: str  # "user" hoặc "assistant"
    content: str
    timestamp: datetime = datetime.now()


class ChatSession(BaseModel):
    """Schema cho một session chat."""
    session_id: str
    messages: List[ChatMessage]
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class ChatHistoryResponse(BaseModel):
    """Schema cho response chat history."""
    session_id: str
    messages: List[Dict[str, str]]
    created_at: datetime
    updated_at: datetime
