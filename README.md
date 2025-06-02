# RAG Pipeline với Langchain và Google Gemini

Dự án này triển khai một RAG (Retrieval-Augmented Generation) Pipeline sử dụng Langchain và Google Gemini để xử lý tài liệu, tạo embeddings, và trả lời câu hỏi dựa trên ngữ cảnh.

## Tính năng chính

- Xử lý tài liệu PDF và TXT
- Tạo embeddings với Google Generative AI
- Lưu trữ vector với ChromaDB
- Reranking kết quả tìm kiếm
- Tạo câu trả lời với Gemini 1.5 Flash
- API RESTful với FastAPI

## Yêu cầu hệ thống

- Python 3.8+
- Google API Key cho Gemini
- Các thư viện Python (xem requirements.txt)

## Cài đặt

1. Clone repository:
```bash
git clone <repository-url>
cd rag-pipeline
```

2. Tạo môi trường ảo:
```bash
python -m venv venv
```

3. Kích hoạt môi trường ảo:
```bash
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

4. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

5. Tạo file .env:
```env
GOOGLE_API_KEY=your_google_api_key_here
```

## Cấu trúc dự án

```
rag-pipeline/
├── app/
│   ├── api/
│   │   ├── endpoints.py
│   │   └── schemas.py
│   ├── models/
│   │   ├── document.py
│   │   ├── embeddings.py
│   │   └── llm.py
│   └── main.py
├── uploads/
│   └── vector_store/
├── .env
├── .gitignore
├── README.md
├── requirements.txt
└── run.py
```

## Sử dụng API

### 1. Upload tài liệu

```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_file.pdf" \
     -F "collection_name=your_collection"
```

### 2. Tạo câu trả lời

```bash
curl -X POST "http://localhost:8000/api/v1/message-generator" \
     -H "Content-Type: application/json" \
     -d '{
           "question": "Câu hỏi của bạn",
           "collection_name": "your_collection"
         }'
```

### 3. Tóm tắt văn bản

```bash
curl -X POST "http://localhost:8000/api/v1/summarize" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "text=Your text here&max_length=200"
```

## Chạy ứng dụng

```bash
python run.py
```

Ứng dụng sẽ chạy tại `http://localhost:8000`

## API Documentation

Sau khi chạy ứng dụng, bạn có thể truy cập:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Các tham số quan trọng

### EmbeddingManager
- `model_name`: "models/embedding-001" (mặc định)
- `persist_directory`: Thư mục lưu trữ vector store

### LLMManager
- `model_name`: "gemini-1.5-flash" (mặc định)
- `temperature`: 0.7 (mặc định)
- `max_output_tokens`: 2048 (mặc định)

### DocumentProcessor
- `chunk_size`: 1000 (mặc định)
- `chunk_overlap`: 200 (mặc định)

## Xử lý lỗi

- Kiểm tra file .env có chứa GOOGLE_API_KEY
- Đảm bảo thư mục uploads/vector_store có quyền ghi
- Kiểm tra định dạng file upload (PDF/TXT)
- Xem logs để biết chi tiết lỗi

## Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng:
1. Fork repository
2. Tạo branch mới
3. Commit changes
4. Push lên branch
5. Tạo Pull Request

## License

MIT License 