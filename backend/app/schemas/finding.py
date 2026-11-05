from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class ReviewActionCreate(BaseModel):
    disposition: str = Field(..., description="CONFIRMED, DISMISSED, or FURTHER_VERIFICATION_NEEDED")
    reason: str = Field(..., description="Reviewer justification")
    actor_id: str = "local_reviewer"

class ReviewActionResponse(BaseModel):
    id: str
    finding_id: str
    actor_id: str
    disposition: str
    reason: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EvidenceLinkResponse(BaseModel):
    id: str
    finding_id: str
    entity_type: str
    entity_id: str
    role: str
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FindingResponse(BaseModel):
    id: str
    case_id: str
    run_id: str
    title: str
    observation_type: str
    severity: str
    uncertainty: str
    summary: str
    alternative_explanations: List[str] = []
    next_recommended_checks: List[str] = []
    reviewer_disposition: str
    reviewer_notes: Optional[str] = None
    reviewer_actor_id: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    evidence_links: List[EvidenceLinkResponse] = []

    model_config = ConfigDict(from_attributes=True)

