# file: app/api/initialization.py

import os
from pathlib import Path
from ..models.document import DocumentProcessor
from ..models.embeddings import EmbeddingManager
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
document_processor = DocumentProcessor()
embedding_manager = EmbeddingManager(
    api_key=api_key,
    persist_directory=str(Path("uploads") / "vector_store")
)

DATA_DIR = Path("data")
DEFAULT_COLLECTION_NAME = "default_collection"

def initialize_vector_store():
    print("🔹 Initializing Vector Store from data/ ...")

    # Lặp qua tất cả các file trong data/
for file_path in DATA_DIR.glob("*.*"):
    print(f"🔸 Processing file: {file_path.name}")

    documents = document_processor.load_document(str(file_path))
    print(f"👉 Loaded {len(documents)} documents")
    for doc in documents:
        print(f"--- Content preview: {doc.page_content[:100]}")  # in 100 ký tự đầu tiên

    # Check documents không rỗng
    if not documents or all(doc.page_content.strip() == "" for doc in documents):
        print(f"⚠️ Skipping {file_path.name} because it's empty or unreadable.")
        continue

    # Tạo vector store
    embedding_manager.create_vector_store(
        documents,
        collection_name=DEFAULT_COLLECTION_NAME
    )


    # Persist vector store
    embedding_manager.persist()

    print(f"✅ Vector store initialized under collection: {DEFAULT_COLLECTION_NAME}")
