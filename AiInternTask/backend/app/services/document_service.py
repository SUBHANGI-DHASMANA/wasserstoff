import os
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import UploadFile
import pypdf
from ..models.document import Document, DocumentMetadata, DocumentPage
from ..core.database import documents_collection
from .ocr_service import OCRService
from .vector_service import VectorService
from ..config import UPLOAD_FOLDER

logger = logging.getLogger(__name__)

class DocumentService:

    @staticmethod
    def save_upload_file(file: UploadFile) -> str:
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        return file_path

    @staticmethod
    def process_pdf(file_path: str) -> List[Dict[str, Any]]:
        try:
            with open(file_path, "rb") as f:
                pdf = pypdf.PdfReader(f)
                pages = []
                extracted_text_empty = True

                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    if text.strip():
                        extracted_text_empty = False
                    pages.append({
                        "page_num": i + 1,
                        "text": text or "No text could be extracted from this page."
                    })

                if extracted_text_empty:
                    try:
                        ocr_pages = OCRService.process_pdf(file_path)
                        if ocr_pages and len(ocr_pages) > 0:
                            return ocr_pages
                    except Exception as ocr_error:
                        logger.warning(f"OCR processing failed, using standard extraction results: {str(ocr_error)}")

                return pages
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return [{
                "page_num": 1,
                "text": f"Error processing PDF: {str(e)}"
            }]

    @staticmethod
    def process_image(file_path: str) -> List[Dict[str, Any]]:
        try:
            text = OCRService.process_image(file_path)
            return [{
                "page_num": 1,
                "text": text
            }]
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return [{
                "page_num": 1,
                "text": f"Error processing image: {str(e)}"
            }]

    @staticmethod
    def create_document(
        file: UploadFile,
        title: str = None
    ) -> Document:
        try:
            file_path = DocumentService.save_upload_file(file)
            file_size = os.path.getsize(file_path)
            filename, file_extension = os.path.splitext(file.filename)
            file_extension = file_extension.lower()
            if not title:
                title = filename
            pages = []
            needs_ocr = False
            if file_extension in ['.pdf']:
                try:
                    needs_ocr = OCRService.is_scanned_document(file_path)
                except Exception as ocr_error:
                    logger.warning(f"Could not check if document needs OCR: {str(ocr_error)}")
                    needs_ocr = False
                pages = DocumentService.process_pdf(file_path)
            elif file_extension in ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp']:
                pages = DocumentService.process_image(file_path)
                needs_ocr = True
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            document_id = str(uuid.uuid4())
            metadata = DocumentMetadata(
                page_count=len(pages),
                processed=True,
                ocr_processed=needs_ocr,
                file_size=file_size,
                upload_date=datetime.now(timezone.utc),
                last_modified=datetime.now(timezone.utc)
            )
            document_pages = []
            for page in pages:
                document_pages.append(DocumentPage(
                    page_num=page["page_num"],
                    text=page["text"]
                ))
            document = Document(
                id=document_id,
                title=title,
                file_type=file_extension[1:],
                original_filename=file.filename,
                metadata=metadata,
                pages=document_pages,
                file_path=file_path
            )

            if documents_collection is None:
                logger.warning("MongoDB documents collection is not initialized")
                logger.info("Skipping MongoDB storage since MongoDB is not available")
                logger.info("Document will only be processed for vector embeddings")

                try:
                    for page in document_pages:
                        embedding_id = VectorService.create_embedding(
                            document_id=document_id,
                            page_num=page.page_num,
                            text=page.text
                        )
                        page.embedding_id = embedding_id
                except Exception as e:
                    logger.error(f"Error creating embeddings: {str(e)}")
            else:
                try:
                    documents_collection.insert_one(document.model_dump(by_alias=True))

                    for page in document_pages:
                        embedding_id = VectorService.create_embedding(
                            document_id=document_id,
                            page_num=page.page_num,
                            text=page.text
                        )
                        page.embedding_id = embedding_id

                    documents_collection.update_one(
                        {"_id": document_id},
                        {"$set": {"pages": [page.model_dump() for page in document_pages]}}
                    )
                except Exception as e:
                    logger.error(f"Error storing document in MongoDB: {str(e)}")

            return document
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            raise

    @staticmethod
    def get_all_documents() -> List[Document]:
        try:
            if documents_collection is None:
                logger.warning("MongoDB documents collection is not initialized")
                return []

            cursor = documents_collection.find()
            documents = []
            for doc_data in cursor:
                try:
                    document = Document(**doc_data)
                    documents.append(document)
                except Exception as doc_error:
                    logger.error(f"Error parsing document: {str(doc_error)}")

            return documents
        except Exception as e:
            logger.error(f"Error getting all documents: {str(e)}")
            return []

    @staticmethod
    def get_document(document_id: str) -> Optional[Document]:
        try:
            if documents_collection is None:
                logger.warning("MongoDB documents collection is not initialized")
                logger.info(f"Cannot retrieve document {document_id} since MongoDB is not available")
                return None

            doc_data = documents_collection.find_one({"_id": document_id})
            if not doc_data:
                return None

            return Document(**doc_data)
        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            return None
