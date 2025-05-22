import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import MONGODB_URI, OLLAMA_API_URL, OLLAMA_MODEL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Initialize MongoDB
from .core.database import initialize_mongodb
mongodb_connected = initialize_mongodb()

from .api.routes import documents, queries

if not mongodb_connected:
    logger.warning("MongoDB Atlas connection failed. The application will run with limited functionality.")

# Check Ollama availability
from .services.ollama_service import OllamaService
if not OllamaService.is_available():
    logger.warning("Ollama is not available. Make sure Ollama is installed and running.")
    logger.warning(f"Trying to connect to Ollama at {OLLAMA_API_URL} with model {OLLAMA_MODEL}")

app = FastAPI(
    title="Document Research Chatbot",
    description="A chatbot for researching across multiple documents",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(queries.router, prefix="/api/queries", tags=["Queries"])

@app.get("/")
def root():
    return {"message": "Welcome to the Document Research Chatbot API"}

@app.get("/health")
def health_check():
    try:
        from .core.database import client
        if client is None:
            mongodb_status = "not configured"
        else:
            client.admin.command('ping')
            mongodb_status = "connected"
    except Exception as e:
        logger.error(f"MongoDB health check failed: {str(e)}")
        mongodb_status = f"error: {str(e)}"

    try:
        from .core.database import document_collection
        collection_count = document_collection.count()
        chroma_status = f"connected (documents: {collection_count})"
    except Exception as e:
        logger.error(f"ChromaDB health check failed: {str(e)}")
        chroma_status = f"error: {str(e)}"

    from .services.ollama_service import OllamaService
    ollama_status = "available" if OllamaService.is_available() else "not available"

    return {
        "status": "healthy",
        "mongodb": mongodb_status,
        "chromadb": chroma_status,
        "ollama": ollama_status,
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
