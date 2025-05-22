# Document Research Chatbot

An interactive chatbot that can perform research across a large set of documents, identify common themes, and provide detailed, cited responses to user queries.

## Features

- **Document Upload and Processing**
  - Support for 75+ documents in various formats (PDF, images)
  - OCR processing for scanned documents
  - Text extraction and storage

- **Document Management**
  - Intuitive interface for viewing uploaded documents
  - Natural language query processing
  - Precise citations (page, paragraph, sentence)

- **Theme Identification**
  - Analysis of responses across documents
  - Identification of common themes
  - Synthesized answers with citations

## Technology Stack

### Backend
- **FastAPI**: Modern, high-performance web framework
- **MongoDB Atlas**: Cloud document database for storing document metadata
- **ChromaDB**: Vector database for semantic search
- **Ollama**: Local LLM for natural language processing
- **Tesseract OCR**: Optical Character Recognition for scanned documents

### Frontend
- **React**: UI library
- **Material-UI**: Component library
- **React Query**: Data fetching and state management
- **Axios**: HTTP client

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   ├── config.py
│   │   └── main.py
│   ├── data/
│   ├── .env
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/
    │   ├── services/
    │   ├── App.jsx
    │   └── main.jsx
    ├── package.json
    └── vite.config.js
```

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB Atlas account
- Tesseract OCR

### Backend Setup

1. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file in the backend directory with the following variables:
```
# MongoDB Atlas Configuration
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster-url>/<dbname>?retryWrites=true&w=majority
MONGODB_DB=document_research_db

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY=data/chroma

# Ollama Configuration
# Ollama runs locally and doesn't require API keys
# Make sure Ollama is installed and running: https://ollama.ai/download
OLLAMA_API_URL=http://localhost:11434/api
# Choose a model that's available in Ollama (run 'ollama list' to see available models)
# Common models: llama2, mistral, gemma, phi
OLLAMA_MODEL=llama2

# Application Configuration
UPLOAD_FOLDER=data/uploads
MAX_UPLOAD_SIZE=50000000  # 50MB
```

3. Start the backend server:
```bash
cd backend
python run.py
```

### Frontend Setup

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

## Usage

1. Access the application at http://localhost:5173
2. Upload documents using the upload form
3. View uploaded documents in the document list
4. Ask questions in the chat interface
5. View responses with citations and identified themes

## MongoDB Atlas Setup

This application is configured to use MongoDB Atlas instead of a local MongoDB instance:

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
