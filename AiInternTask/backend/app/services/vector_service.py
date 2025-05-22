import logging
import os
from typing import List, Dict, Any
from ..core.database import document_collection

os.environ["TOKENIZERS_PARALLELISM"] = "false"

logger = logging.getLogger(__name__)

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    logger.warning("HuggingFace embeddings not available. Vector search will be limited.")

class VectorService:
    embedding_model = None
    if HUGGINGFACE_AVAILABLE:
        try:
            embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True}
            )
        except Exception as e:
            logger.error(f"Error initializing HuggingFaceEmbeddings: {str(e)}")

    @staticmethod
    def create_embedding(document_id: str, page_num: int, text: str) -> str:
        embedding_id = f"{document_id}_page_{page_num}"

        if not VectorService.embedding_model:
            logger.warning("Embedding model not available. Skipping vector embedding creation.")
            return embedding_id

        try:
            embeddings = VectorService.embedding_model.embed_documents([text])
            if not embeddings:
                raise ValueError("Embedding failed or returned empty result.")
            embedding = embeddings[0]

            doc_id_str = str(document_id)

            document_collection.add(
                ids=[embedding_id],
                embeddings=[embedding],
                metadatas=[{
                    "document_id": doc_id_str,
                    "page_num": page_num
                }],
                documents=[text]
            )
            return embedding_id
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            return embedding_id

    @staticmethod
    def search_similar_documents(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not VectorService.embedding_model:
            logger.warning("Embedding model not available. Returning empty search results.")
            return []

        try:
            collection_count = document_collection.count()
            if collection_count == 0:
                logger.warning("ChromaDB collection is empty. No embeddings to search.")
                return []

            query_embedding = VectorService.embedding_model.embed_query(query)

            actual_top_k = min(top_k, collection_count)
            if actual_top_k < top_k:
                logger.info(f"Limiting search results to {actual_top_k} (collection size) instead of requested {top_k}")

            results = document_collection.query(
                query_embeddings=[query_embedding],
                n_results=actual_top_k,
                include=["metadatas", "documents", "distances"]
            )

            formatted_results = []
            if results["ids"] and len(results["ids"][0]) > 0:
                for i in range(len(results["ids"][0])):
                    metadata = results["metadatas"][0][i] if i < len(results["metadatas"][0]) else {}
                    document_id = metadata.get("document_id", "unknown")
                    page_num = metadata.get("page_num", 1)

                    text = results["documents"][0][i] if i < len(results["documents"][0]) else ""

                    distance = results["distances"][0][i] if i < len(results["distances"][0]) else 1.0
                    similarity_score = 1.0 - distance

                    formatted_results.append({
                        "document_id": document_id,
                        "page_num": page_num,
                        "text": text,
                        "similarity_score": similarity_score
                    })

                logger.info(f"Found {len(formatted_results)} similar documents")
            else:
                logger.warning("No similar documents found in vector search")

            return formatted_results
        except Exception as e:
            logger.error(f"Error searching similar documents: {str(e)}")
            return []

    @staticmethod
    def rebuild_embeddings_for_document(document_id: str) -> bool:
        if not VectorService.embedding_model:
            logger.warning("Embedding model not available. Cannot rebuild embeddings.")
            return False

        try:
            from ..core.database import documents_collection

            if documents_collection is None:
                logger.warning("MongoDB documents collection is not initialized")
                logger.info("Cannot rebuild embeddings without MongoDB connection")
                return False

            doc_data = documents_collection.find_one({"_id": document_id})
            if not doc_data:
                logger.warning(f"Document {document_id} not found in MongoDB")
                return False

            try:
                results = document_collection.get(
                    where={"document_id": str(document_id)}
                )

                if results and results["ids"]:
                    document_collection.delete(
                        ids=results["ids"]
                    )
                    logger.info(f"Deleted {len(results['ids'])} existing embeddings for document {document_id}")
            except Exception as e:
                logger.error(f"Error deleting existing embeddings: {str(e)}")
            from ..models.document import Document
            document = Document(**doc_data)

            for page in document.pages:
                embedding_id = VectorService.create_embedding(
                    document_id=document_id,
                    page_num=page.page_num,
                    text=page.text
                )
                page.embedding_id = embedding_id

            documents_collection.update_one(
                {"_id": document_id},
                {"$set": {"pages": [page.model_dump() for page in document.pages]}}
            )

            logger.info(f"Successfully rebuilt embeddings for document {document_id}")
            return True

        except Exception as e:
            logger.error(f"Error rebuilding embeddings: {str(e)}")
            return False
