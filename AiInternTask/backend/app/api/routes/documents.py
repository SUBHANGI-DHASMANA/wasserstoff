from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import List, Dict, Any
import logging
from ...models.document import DocumentResponse
from ...services.document_service import DocumentService
from ...services.vector_service import VectorService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    title: str = Form(None)
):
    try:
        from ...core.database import client
        if client is None:
            logger.warning("MongoDB is not available. Document will be processed but not stored in MongoDB.")

        document = DocumentService.create_document(file, title)
        return DocumentResponse(
            id=document.id,
            title=document.title,
            file_type=document.file_type,
            original_filename=document.original_filename,
            page_count=document.metadata.page_count,
            processed=document.metadata.processed,
            ocr_processed=document.metadata.ocr_processed,
            file_size=document.metadata.file_size,
            upload_date=document.metadata.upload_date,
            last_modified=document.metadata.last_modified
        )
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading document: {str(e)}"
        )

@router.get("/", response_model=List[DocumentResponse])
def get_all_documents():
    try:
        from ...core.database import client
        if client is None:
            logger.warning("MongoDB is not available. Returning empty document list.")
            return []

        documents = DocumentService.get_all_documents()
        return [
            DocumentResponse(
                id=doc.id,
                title=doc.title,
                file_type=doc.file_type,
                original_filename=doc.original_filename,
                page_count=doc.metadata.page_count,
                processed=doc.metadata.processed,
                ocr_processed=doc.metadata.ocr_processed,
                file_size=doc.metadata.file_size,
                upload_date=doc.metadata.upload_date,
                last_modified=doc.metadata.last_modified
            )
            for doc in documents
        ]
    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}")
        return []

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str):
    try:
        from ...core.database import client
        if client is None:
            logger.warning("MongoDB is not available. Cannot retrieve document.")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable"
            )

        document = DocumentService.get_document(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        return DocumentResponse(
            id=document.id,
            title=document.title,
            file_type=document.file_type,
            original_filename=document.original_filename,
            page_count=document.metadata.page_count,
            processed=document.metadata.processed,
            ocr_processed=document.metadata.ocr_processed,
            file_size=document.metadata.file_size,
            upload_date=document.metadata.upload_date,
            last_modified=document.metadata.last_modified
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting document: {str(e)}"
        )

@router.post("/{document_id}/rebuild-embeddings", response_model=Dict[str, Any])
def rebuild_document_embeddings(document_id: str):
    try:
        from ...core.database import client
        if client is None:
            logger.warning("MongoDB is not available. Cannot rebuild embeddings.")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable"
            )

        success = VectorService.rebuild_embeddings_for_document(document_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to rebuild embeddings for document {document_id}"
            )
        return {
            "success": True,
            "message": f"Successfully rebuilt embeddings for document {document_id}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rebuilding embeddings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error rebuilding embeddings: {str(e)}"
        )
