from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict

class FieldRevisionCreate(BaseModel):
    new_value: str
    reason: str
    expected_revision_num: int
    actor_id: str = "local_reviewer"

class FieldRevisionResponse(BaseModel):
    id: str
    field_id: str
    revision_number: int
    actor_id: str
    reason: str
    previous_value: str
    new_value: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FieldResponse(BaseModel):
    id: str
    run_id: str
    page_id: str
    field_name: str
    raw_value: str
    normalized_value: Optional[str] = None
    numeric_value: Optional[float] = None
    currency: str
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    bbox_normalized: List[float]  # [ymin, xmin, ymax, xmax]
    bbox_original: Optional[Dict[str, Any]] = None
    extractor_name: str
    extractor_version: str
    extraction_score: float
    current_revision_num: int
    created_at: datetime
    revisions: List[FieldRevisionResponse] = []

    model_config = ConfigDict(from_attributes=True)

class ClaimResponse(BaseModel):
    id: str
    run_id: str
    claim_type: str
    subject: str
    basis: str
    amount: Optional[float] = None
    currency: str
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    status: str
    supporting_field_ids: List[str] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TransactionResponse(BaseModel):
    id: str
    run_id: str
    page_id: str
    transaction_date: str
    narration: str
    transaction_type: str
    amount: float
    running_balance: Optional[float] = None
    is_salary_candidate: int
    bbox_normalized: Optional[List[float]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

