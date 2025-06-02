"""
Module quản lý lịch sử chat.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Optional
from ..api.schemas import ChatMessage, ChatSession


class ChatHistoryManager:
    def __init__(self):
        """Khởi tạo ChatHistoryManager."""
        self.sessions: Dict[str, ChatSession] = {}

    def create_session(self) -> str:
        """
        Tạo session mới.

        Returns:
            str: ID của session mới
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = ChatSession(
            session_id=session_id,
            messages=[]
        )
        return session_id

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> Optional[ChatSession]:
        """
        Thêm tin nhắn vào session.

        Args:
            session_id: ID của session
            role: Vai trò ("user" hoặc "assistant")
            content: Nội dung tin nhắn

        Returns:
            Optional[ChatSession]: Session đã được cập nhật
        """
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now()
        )
        session.messages.append(message)
        session.updated_at = datetime.now()
        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Lấy thông tin session.

        Args:
            session_id: ID của session

        Returns:
            Optional[ChatSession]: Thông tin session
        """
        return self.sessions.get(session_id)

    def get_chat_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> Optional[List[Dict[str, str]]]:
        """
        Lấy lịch sử chat của session.

        Args:
            session_id: ID của session
            limit: Số lượng tin nhắn tối đa

        Returns:
            Optional[List[Dict[str, str]]]: Lịch sử chat
        """
        session = self.get_session(session_id)
        if not session:
            return None

        messages = session.messages
        if limit:
            messages = messages[-limit:]

        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]

    def delete_session(self, session_id: str) -> bool:
        """
        Xóa session.

        Args:
            session_id: ID của session

        Returns:
            bool: True nếu xóa thành công
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
