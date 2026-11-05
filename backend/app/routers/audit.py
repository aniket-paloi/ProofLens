from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.audit import verify_case_audit_chain
from backend.app.models.case import Case
from backend.app.models.finding import AuditEvent
from backend.app.schemas.audit import AuditEventResponse, AuditVerificationResponse

router = APIRouter(tags=["Audit & Integrity"])

@router.get("/cases/{case_id}/audit", response_model=List[AuditEventResponse])
def get_case_audit_trail(case_id: str, db: Session = Depends(get_db)):
    c = db.query(Case).filter(Case.id == case_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
        
    return (
        db.query(AuditEvent)
        .filter(AuditEvent.case_id == case_id)
        .order_by(AuditEvent.sequence_number.asc())
        .all()
    )

@router.post("/cases/{case_id}/audit/verify", response_model=AuditVerificationResponse)
def verify_audit_trail(case_id: str, db: Session = Depends(get_db)):
    c = db.query(Case).filter(Case.id == case_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
        
    is_valid, msg, count = verify_case_audit_chain(db, case_id)
    last_event = (
        db.query(AuditEvent)
        .filter(AuditEvent.case_id == case_id)
        .order_by(AuditEvent.sequence_number.desc())
        .first()
    )
    last_hash = last_event.current_event_hash if last_event else ("0" * 64)
    
    return AuditVerificationResponse(
        case_id=case_id,
        total_events=count,
        chain_valid=is_valid,
        last_verified_hash=last_hash,
        verified_at=datetime.now(timezone.utc),
        message=msg
    )

