# Document Research Chatbot Backend

This is the backend for the Document Research Chatbot, built with FastAPI, MongoDB Atlas, ChromaDB, and Ollama.

## Features

- Document upload and processing
- OCR for scanned documents
- Vector embeddings for semantic search
- Query processing with detailed citations
- Theme identification across documents

## Requirements

- Python 3.8+
- MongoDB Atlas account
- Tesseract OCR

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up environment variables:

Create a `.env` file in the backend directory with the following variables (copy from `.env.example`):

```
# MongoDB Atlas Configuration
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster-url>/<dbname>?retryWrites=true&w=majority
MONGODB_DB=document_research_db

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY=data/chroma

# Ollama Configuration
# Ollama runs locally and doesn't require API keys
OLLAMA_API_URL=http://localhost:11434/api
# Choose a model that's available in Ollama
OLLAMA_MODEL=llama2

# Application Configuration
UPLOAD_FOLDER=data/uploads
MAX_UPLOAD_SIZE=50000000  # 50MB
```

## MongoDB Atlas Setup

1. Create a MongoDB Atlas account at https://www.mongodb.com/cloud/atlas/register
2. Create a new cluster (the free tier is sufficient for testing)
3. Create a database user with read/write privileges
4. Add your IP address to the IP access list
5. Get your connection string from the Atlas dashboard
6. Update the `MONGODB_URI` in your `.env` file with your connection details

## Ollama Setup

1. Install Ollama from https://ollama.ai/download
2. Run Ollama locally
3. Pull the model you want to use (e.g., `ollama pull llama2`)
4. Make sure Ollama is running when you start the application
5. You can customize the model by updating the `OLLAMA_MODEL` in your `.env` file

## Running the Application

```bash
python run.py
```

Or with uvicorn directly:

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000.

## API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── documents.py
│   │       └── queries.py
│   ├── core/
│   │   └── database.py
│   ├── models/
│   │   ├── document.py
│   │   └── query.py
│   ├── services/
│   │   ├── document_service.py
│   │   ├── ocr_service.py
│   │   ├── ollama_service.py
│   │   ├── query_service.py
│   │   ├── theme_service.py
│   │   └── vector_service.py
│   ├── config.py
│   └── main.py
├── data/
│   ├── chroma/
│   └── uploads/
├── .env
├── requirements.txt
└── run.py
```
