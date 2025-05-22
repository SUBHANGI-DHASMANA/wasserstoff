import pymongo
import chromadb
import logging
from chromadb.config import Settings
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ..config import MONGODB_URI, MONGODB_DB, CHROMA_PERSIST_DIRECTORY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MongoDB and collections
client = None
database = None
documents_collection = None
queries_collection = None

def initialize_mongodb():
    global client, database, documents_collection, queries_collection
    try:
        if "<username>" in MONGODB_URI or "<password>" in MONGODB_URI or "<cluster-url>" in MONGODB_URI:
            return False

        client = pymongo.MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=45000,
            maxPoolSize=100,
            retryWrites=True
        )
        client.admin.command('ping')
        logger.info("Connected to MongoDB Atlas successfully")

        database = client[MONGODB_DB]
        documents_collection = database.documents
        queries_collection = database.queries
        return True

    except Exception as e:
        logger.error(f"Failed to connect to MongoDB Atlas: {str(e)}")
        return False

# ChromaDB client
chroma_client = chromadb.PersistentClient(
    path=CHROMA_PERSIST_DIRECTORY,
    settings=Settings(anonymized_telemetry=False)
)

document_collection = chroma_client.get_or_create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}
)

def get_document_by_id(document_id: str):
    if documents_collection is None:
        raise RuntimeError("MongoDB not initialized. Call initialize_mongodb() first.")
    return documents_collection.find_one({"_id": document_id})

def get_all_documents():
    if documents_collection is None:
        raise RuntimeError("MongoDB not initialized. Call initialize_mongodb() first.")
    cursor = documents_collection.find()
    return list(cursor)
