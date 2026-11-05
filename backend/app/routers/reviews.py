from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.audit import record_audit_event
from backend.app.models.field import Field, FieldRevision
from backend.app.models.finding import Finding, ReviewAction
from backend.app.schemas.field import FieldRevisionCreate, FieldRevisionResponse
from backend.app.schemas.finding import ReviewActionCreate, ReviewActionResponse

router = APIRouter(tags=["Reviewer Corrections & Dispositions"])

@router.post("/fields/{field_id}/revisions", response_model=FieldRevisionResponse, status_code=status.HTTP_201_CREATED)
def create_field_revision(
    field_id: str,
    rev_in: FieldRevisionCreate,
    db: Session = Depends(get_db)
):
    f = db.query(Field).filter(Field.id == field_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Field not found")
        
    # Optimistic concurrency check
    if f.current_revision_num != rev_in.expected_revision_num:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Revision conflict: current revision is {f.current_revision_num}, expected {rev_in.expected_revision_num}"
        )
        
    new_rev_num = f.current_revision_num + 1
    prev_val = f.normalized_value or f.raw_value
    
    # Try converting to numeric if applicable
    numeric_val = None
    try:
        clean_num = rev_in.new_value.replace(",", "").replace("$", "").replace("₹", "").strip()
        numeric_val = float(clean_num)
    except ValueError:
        pass
        
    revision = FieldRevision(
        field_id=field_id,
        revision_number=new_rev_num,
        actor_id=rev_in.actor_id,
        reason=rev_in.reason,
        previous_value=prev_val,
        new_value=rev_in.new_value,
        new_numeric_value=numeric_val
    )
    
    # Update field current state
    f.normalized_value = rev_in.new_value
    if numeric_val is not None:
        f.numeric_value = numeric_val
    f.current_revision_num = new_rev_num
    
    db.add(revision)
    db.commit()
    db.refresh(revision)
    
    # Audit log with case context
    case_id = f.run.case_id if f.run else "unknown_case"
    record_audit_event(
        db=db,
        case_id=case_id,
        action_type="FIELD_REVISED",
        actor_id=rev_in.actor_id,
        payload={
            "field_id": field_id,
            "revision_number": new_rev_num,
            "previous_value": prev_val,
            "new_value": rev_in.new_value,
            "reason": rev_in.reason
        }
    )
    return revision

@router.post("/findings/{finding_id}/reviews", response_model=ReviewActionResponse, status_code=status.HTTP_201_CREATED)
def submit_finding_review(
    finding_id: str,
    rev_in: ReviewActionCreate,
    db: Session = Depends(get_db)
):
    f = db.query(Finding).filter(Finding.id == finding_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Finding not found")
        
    action = ReviewAction(
        finding_id=finding_id,
        actor_id=rev_in.actor_id,
        disposition=rev_in.disposition,
        reason=rev_in.reason
    )
    
    f.reviewer_disposition = rev_in.disposition
    f.reviewer_notes = rev_in.reason
    f.reviewer_actor_id = rev_in.actor_id
    f.reviewed_at = datetime.now(timezone.utc)
    
    db.add(action)
    db.commit()
    db.refresh(action)
    
    record_audit_event(
        db=db,
        case_id=f.case_id,
        action_type="FINDING_REVIEWED",
        actor_id=rev_in.actor_id,
        payload={
            "finding_id": finding_id,
            "disposition": rev_in.disposition,
            "reason": rev_in.reason
        }
    )
    return action

