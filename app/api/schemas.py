"""
Schema cho API endpoints.
"""

from pydantic import BaseModel
from typing import Optional


class MessageRequest(BaseModel):
    """Schema cho request tạo message."""
    question: str
    file_path: Optional[str] = None


class MessageResponse(BaseModel):
    """Schema cho response message."""
    answer: str
    context: Optional[str] = None
