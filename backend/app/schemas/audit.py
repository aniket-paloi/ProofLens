from datetime import datetime
from pydantic import BaseModel, ConfigDict

class AuditEventResponse(BaseModel):
    id: str
    case_id: str
    sequence_number: int
    action_type: str
    actor_id: str
    payload_json: str
    previous_event_hash: str
    current_event_hash: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AuditVerificationResponse(BaseModel):
    case_id: str
    total_events: int
    chain_valid: bool
    last_verified_hash: str
    verified_at: datetime
    message: str

