from datetime import datetime, timezone
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        from bson import ObjectId
        yield cls.validate

    @classmethod
    def validate(cls, v):
        from bson import ObjectId
        if not ObjectId.is_valid(v):
            if not isinstance(v, str):
                raise ValueError("Invalid ObjectId")
        return str(v)

class DocumentBase(BaseModel):
    title: str
    file_type: str
    original_filename: str

class DocumentCreate(DocumentBase):
    pass

class DocumentMetadata(BaseModel):
    page_count: int
    processed: bool = False
    ocr_processed: bool = False
    file_size: int
    upload_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DocumentPage(BaseModel):
    page_num: int
    text: str
    embedding_id: Optional[str] = None

class Document(DocumentBase):
    id: Union[str, PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    metadata: DocumentMetadata
    pages: List[DocumentPage] = []
    file_path: str

    model_config = {
        "populate_by_name": True,
        "validate_by_name": True,
        "json_encoders": {
            PyObjectId: str
        }
    }

class DocumentResponse(BaseModel):
    id: str
    title: str
    file_type: str
    original_filename: str
    page_count: int
    processed: bool
    ocr_processed: bool
    file_size: int
    upload_date: datetime
    last_modified: datetime
