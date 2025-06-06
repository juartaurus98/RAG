"""
API endpoints cho RAG Pipeline.
"""

import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Optional
from dotenv import load_dotenv
import shutil
from pathlib import Path

from ..models.document import DocumentProcessor
from ..models.embeddings import EmbeddingManager
from ..models.llm import LLMManager
from ..models.chat_history import ChatHistoryManager
from .schemas import (
    MessageRequest,
    MessageResponse,
    ChatHistoryResponse
)

# Load environment variables
load_dotenv()

router = APIRouter()
api_key = os.getenv("GOOGLE_API_KEY")

# Tạo thư mục lưu trữ
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Khởi tạo các managers
document_processor = DocumentProcessor()
embedding_manager = EmbeddingManager(
    api_key=api_key,
    persist_directory=str(UPLOAD_DIR / "vector_store")
)
llm_manager = LLMManager(api_key)
chat_history_manager = ChatHistoryManager()


@router.post("/message-generator", response_model=MessageResponse)
async def generate_message(
    request: MessageRequest,
    custom_prompt: Optional[str] = None,
    max_tokens: Optional[int] = None,
    collection_name: Optional[str] = None
) -> Dict:
    """
    Endpoint tạo message dựa trên câu hỏi và dữ liệu từ ChromaDB.

    Args:
        request: Request chứa câu hỏi
        custom_prompt: Prompt tùy chỉnh cho LLM
        max_tokens: Số token tối đa cho output
        collection_name: Tên collection trong ChromaDB

    Returns:
        MessageResponse: Response chứa câu trả lời và context
    """
    try:
        print("Bắt đầu xử lý request:", request)
        # Tạo session mới nếu chưa có
        if not request.session_id:
            request.session_id = chat_history_manager.create_session()

        # Lưu câu hỏi vào chat history
        chat_history_manager.add_message(
            session_id=request.session_id,
            role="user",
            content=request.question
        )

        print("Đã thêm message vào history")
        # Load vector store từ ChromaDB
        if collection_name:
            embedding_manager.load_vector_store(
                collection_name=collection_name)
        else:
            embedding_manager.load_vector_store(collection_name="default_collection")

        print("Đã load vector store")
        # Lấy retriever và thực hiện reranking
        base_retriever = embedding_manager.get_retriever(
            k=5,
            search_type="mmr"  # Sử dụng MMR để đa dạng kết quả
        )
        reranker = llm_manager.setup_reranker(base_retriever)

        # Lấy relevant documents
        relevant_docs = reranker.get_relevant_documents(request.question)
        context = "\n".join([doc.page_content for doc in relevant_docs])

        # Tạo câu trả lời
        kwargs = {}
        if max_tokens:
            kwargs["max_output_tokens"] = max_tokens

        answer = llm_manager.generate_response(
            question=request.question,
            context=context,
            custom_prompt=custom_prompt,
            **kwargs
        )

        # Lưu câu trả lời vào chat history
        chat_history_manager.add_message(
            session_id=request.session_id,
            role="assistant",
            content=answer
        )

        return MessageResponse(
            answer=answer,
            context=context,
            session_id=request.session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat-history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    limit: Optional[int] = None
) -> Dict:
    """
    Lấy lịch sử chat của một session.

    Args:
        session_id: ID của session
        limit: Số lượng tin nhắn tối đa

    Returns:
        ChatHistoryResponse: Lịch sử chat
    """
    try:
        session = chat_history_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )

        messages = chat_history_manager.get_chat_history(
            session_id=session_id,
            limit=limit
        )

        return ChatHistoryResponse(
            session_id=session_id,
            messages=messages,
            created_at=session.created_at,
            updated_at=session.updated_at
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat-history/{session_id}")
async def delete_chat_history(session_id: str) -> Dict:
    """
    Xóa lịch sử chat của một session.

    Args:
        session_id: ID của session

    Returns:
        Dict: Thông báo kết quả
    """
    try:
        success = chat_history_manager.delete_session(session_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )

        return {"message": "Chat history deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    collection_name: Optional[str] = None
) -> Dict:
    """
    Upload và xử lý file.

    Args:
        file: File cần upload
        collection_name: Tên collection cho vector store

    Returns:
        Dict: Thông tin về file đã upload
    """
    try:
        # Lưu file
        file_path = UPLOAD_DIR / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Xử lý document
        documents = document_processor.load_document(str(file_path))

        # Tạo vector store
        collection = collection_name or Path(file.filename).stem
        embedding_manager.create_vector_store(
            documents,
            collection_name=collection
        )

        # Lưu vector store
        embedding_manager.persist()

        return {
            "message": "File uploaded and processed successfully",
            "filename": file.filename,
            "collection": collection
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize")
async def summarize_text(
    text: str = Form(...),
    max_length: int = Form(200)
) -> Dict:
    """
    Tạo tóm tắt cho văn bản.

    Args:
        text: Văn bản cần tóm tắt
        max_length: Độ dài tối đa của tóm tắt

    Returns:
        Dict: Tóm tắt được tạo ra
    """
    try:
        summary = llm_manager.generate_summary(
            text=text,
            max_length=max_length
        )
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
