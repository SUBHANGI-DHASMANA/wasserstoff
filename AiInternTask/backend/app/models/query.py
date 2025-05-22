from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class QueryBase(BaseModel):
    text: str

class QueryCreate(QueryBase):
    pass

class DocumentCitation(BaseModel):
    document_id: str
    document_title: str
    page_number: Optional[int] = None
    paragraph: Optional[int] = None
    sentence: Optional[str] = None
    relevance_score: float

class DocumentResponse(BaseModel):
    document_id: str
    document_title: str
    extracted_answer: str
    citations: List[DocumentCitation]

class ThemeResponse(BaseModel):
    theme_name: str
    description: str
    document_ids: List[str]
    supporting_evidence: List[str]

class QueryResponse(BaseModel):
    id: str
    query_text: str
    document_responses: List[DocumentResponse]
    themes: List[ThemeResponse]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Query(QueryBase):
    id: str
    document_responses: List[DocumentResponse] = []
    themes: List[ThemeResponse] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
