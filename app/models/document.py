"""
Module xử lý document từ các file PDF và TXT.
"""
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredFileLoader
from langchain_community.document_loaders.base import BaseLoader
from typing import List, Optional


class DocumentProcessor:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None
    ):
        """
        Khởi tạo DocumentProcessor.

        Args:
            chunk_size: Kích thước mỗi chunk
            chunk_overlap: Độ chồng lấp giữa các chunk
            separators: Danh sách các ký tự phân tách
        """
        if separators is None:
            separators = ["\n\n", "\n", " ", ""]

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
            is_separator_regex=False
        )

    def _get_loader(self, file_path: str) -> BaseLoader:
        """
        Lấy loader phù hợp cho file.

        Args:
            file_path: Đường dẫn đến file

        Returns:
            BaseLoader: Loader phù hợp cho file
        """
        if file_path.endswith('.pdf'):
            return PyPDFLoader(file_path)
        elif file_path.endswith('.txt'):
            return TextLoader(file_path, encoding='utf-8')
        else:
            # Sử dụng UnstructuredFileLoader cho các định dạng khác
            return UnstructuredFileLoader(file_path)

    def load_document(self, file_path: str) -> List[Document]:
        """
        Đọc và xử lý tài liệu từ file.

        Args:
            file_path: Đường dẫn đến file cần đọc

        Returns:
            List[Document]: Danh sách các document đã được xử lý
        """
        try:
            loader = self._get_loader(file_path)
            documents = loader.load()
            return self.text_splitter.split_documents(documents)
        except Exception as e:
            raise ValueError(f"Lỗi khi đọc file {file_path}: {str(e)}")

    def load_documents(self, file_paths: List[str]) -> List[Document]:
        """
        Đọc và xử lý nhiều tài liệu.

        Args:
            file_paths: Danh sách đường dẫn đến các file

        Returns:
            List[Document]: Danh sách các document đã được xử lý
        """
        all_documents = []
        for file_path in file_paths:
            documents = self.load_document(file_path)
            all_documents.extend(documents)
        return all_documents
