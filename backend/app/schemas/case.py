from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class PageResponse(BaseModel):
    id: str
    page_number: int
    width_pts: float
    height_pts: float
    rotation_deg: int
    has_native_text: int
    rendered_image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class DocumentResponse(BaseModel):
    id: str
    case_id: str
    filename: str
    mime_type: str
    file_size_bytes: int
    sha256_hash: str
    classified_type: str
    classification_confidence: float
    page_count: int
    created_at: datetime
    pages: List[PageResponse] = []

    model_config = ConfigDict(from_attributes=True)

class CaseCreate(BaseModel):
    reference_number: str = Field(..., description="Unique case reference code")
    applicant_name: str = Field(..., description="Full name of applicant")

class CaseResponse(BaseModel):
    id: str
    reference_number: str
    applicant_name: str
    status: str
    created_at: datetime
    updated_at: datetime
    documents: List[DocumentResponse] = []

    model_config = ConfigDict(from_attributes=True)

class ProcessingRunResponse(BaseModel):
    id: str
    case_id: str
    status: str
    snapshot_hash: str
    config_version: str
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

