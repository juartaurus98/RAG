"""
Module xử lý embeddings và vector store.
"""

from typing import List, Optional, Dict, Any
import os
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.vectorstores import VectorStore
from app.config import GOOGLE_API_KEY


class EmbeddingManager:
    def __init__(
        self,
        api_key: str = GOOGLE_API_KEY,
        model_name: str = "models/embedding-001",
        persist_directory: Optional[str] = None
    ):
        """
        Khởi tạo EmbeddingManager.

        Args:
            api_key: Google API key
            model_name: Tên model embedding
            persist_directory: Thư mục lưu trữ vector store
        """
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=model_name,
            google_api_key=api_key
        )
        self.persist_directory = persist_directory
        self.vector_store = None

    def create_vector_store(
        self,
        documents: List[Document],
        collection_name: str = "documents"
    ) -> VectorStore:
        """
        Tạo vector store từ documents.

        Args:
            documents: Danh sách các document cần lưu trữ
            collection_name: Tên collection trong vector store

        Returns:
            VectorStore: Vector store đã được tạo
        """
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=collection_name
        )
        return self.vector_store

    def load_vector_store(
        self,
        collection_name: str = "documents"
    ) -> VectorStore:
        """
        Load vector store từ disk.

        Args:
            collection_name: Tên collection cần load

        Returns:
            VectorStore: Vector store đã được load
        """
        if not self.persist_directory:
            raise ValueError("persist_directory chưa được cấu hình")

        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=collection_name
        )
        return self.vector_store

    def get_retriever(
        self,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        search_type: str = "similarity"
    ):
        """
        Lấy retriever từ vector store.

        Args:
            k: Số lượng kết quả trả về
            filter: Bộ lọc cho kết quả
            search_type: Loại tìm kiếm ("similarity" hoặc "mmr")

        Returns:
            Retriever từ vector store
        """
        if not self.vector_store:
            raise ValueError("Vector store chưa được khởi tạo")

        return self.vector_store.as_retriever(
            search_kwargs={
                "k": k,
                "filter": filter
            },
            search_type=search_type
        )

    def persist(self):
        """Lưu vector store xuống disk."""
        if self.vector_store and self.persist_directory:
            self.vector_store.persist()
