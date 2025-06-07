"""
Main application file cho FastAPI.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.initialization import initialize_vector_store

from .api.endpoints import router

app = FastAPI(
    title="RAG Pipeline API",
    description="API cho RAG Pipeline sử dụng Langchain và Google Gemini",
    version="1.0.0",
    debug= True
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thêm router
app.include_router(router, prefix="/api/v1")
initialize_vector_store()
