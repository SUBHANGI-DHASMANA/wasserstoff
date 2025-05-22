import logging
import uuid
import os
from typing import Optional, List, Dict, Any
from ..models.query import Query, QueryCreate, DocumentResponse, DocumentCitation
from ..models.document import Document
from ..core.database import queries_collection, documents_collection
from .vector_service import VectorService
from .ollama_service import OllamaService

os.environ["TOKENIZERS_PARALLELISM"] = "false"

logger = logging.getLogger(__name__)

class QueryService:
    @staticmethod
    def create_query(query_create: QueryCreate) -> Query:
        try:
            query_id = str(uuid.uuid4())

            try:
                similar_docs = VectorService.search_similar_documents(query_create.text, top_k=10)

                document_ids = list(set([doc["document_id"] for doc in similar_docs]))

                if document_ids:
                    logger.info(f"Vector search found {len(document_ids)} relevant documents")
                else:
                    logger.warning("No documents found via vector search. Falling back to all documents.")
            except Exception as vector_error:
                logger.error(f"Error during vector search: {str(vector_error)}. Falling back to all documents.")
                document_ids = []

            if not document_ids:
                try:
                    all_docs = list(documents_collection.find())
                    document_ids = [str(doc["_id"]) for doc in all_docs]
                    logger.info(f"Using all {len(document_ids)} documents")
                except Exception as db_error:
                    logger.error(f"Error getting documents: {str(db_error)}")
                    document_ids = []

            document_responses = []
            for doc_id in document_ids:
                try:
                    doc_data = documents_collection.find_one({"_id": doc_id})
                    if not doc_data:
                        logger.warning(f"Document {doc_id} not found in MongoDB")
                        continue

                    document = Document(**doc_data)

                    document_text = "\n\n".join([f"Page {page.page_num}:\n{page.text}" for page in document.pages])

                    if OllamaService.is_available():
                        result = OllamaService.extract_answer_from_document(document_text, query_create.text)
                    else:
                        logger.warning("Ollama is not available. Using simple text extraction.")
                        result = {
                            "extracted_answer": f"Ollama is not available. Here's a preview of the document:\n\n{document_text[:500]}...",
                            "citations": []
                        }

                    citations = []
                    for citation in result.get("citations", []):
                        citations.append(DocumentCitation(
                            document_id=doc_id,
                            document_title=document.title,
                            page_number=citation.get("page_number"),
                            paragraph=citation.get("paragraph"),
                            sentence=citation.get("sentence"),
                            relevance_score=citation.get("relevance_score", 0.5)
                        ))

                    document_responses.append(DocumentResponse(
                        document_id=doc_id,
                        document_title=document.title,
                        extracted_answer=result.get("extracted_answer", "No answer extracted"),
                        citations=citations
                    ))

                except Exception as doc_error:
                    logger.error(f"Error processing document {doc_id}: {str(doc_error)}")
                    document_responses.append(DocumentResponse(
                        document_id=doc_id,
                        document_title=f"Document {doc_id}",
                        extracted_answer=f"Error processing document: {str(doc_error)}",
                        citations=[]
                    ))

            query = Query(
                id=query_id,
                text=query_create.text,
                document_responses=document_responses,
                themes=[]
            )

            query_dict = query.model_dump(by_alias=True)
            query_dict['_id'] = query_id
            queries_collection.insert_one(query_dict)

            return query
        except Exception as e:
            logger.error(f"Error creating query: {str(e)}")
            raise

    @staticmethod
    def get_query(query_id: str) -> Optional[Query]:
        try:
            if queries_collection is None:
                logger.error(f"Cannot get query {query_id}: MongoDB connection not available")
                return None

            logger.info(f"Attempting to retrieve query with ID: {query_id}")

            query_data = queries_collection.find_one({"_id": query_id})

            if not query_data:
                logger.error(f"Query with ID {query_id} not found in MongoDB")
                return None

            logger.info(f"Found query with ID {query_id}")

            return Query(**query_data)
        except Exception as e:
            logger.error(f"Error getting query {query_id}: {str(e)}", exc_info=True)
            return None
