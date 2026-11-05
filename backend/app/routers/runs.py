import hashlib
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.audit import record_audit_event
from backend.app.models.case import Case
from backend.app.models.field import Field, Claim, Transaction
from backend.app.models.execution import ProcessingRun, CheckExecution
from backend.app.models.finding import Finding
from backend.app.schemas.case import ProcessingRunResponse
from backend.app.schemas.field import FieldResponse, ClaimResponse, TransactionResponse
from backend.app.schemas.finding import FindingResponse
from backend.worker.local_runner import process_run

router = APIRouter(tags=["Processing Runs & Intelligence"])

@router.post("/cases/{case_id}/runs", response_model=ProcessingRunResponse, status_code=status.HTTP_201_CREATED)
def trigger_processing_run(
    case_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    doc_hashes = [d.sha256_hash for d in case.documents]
    snapshot = (
        hashlib.sha256(("".join(sorted(doc_hashes))).encode('utf-8')).hexdigest()
        if doc_hashes
        else "empty_snapshot"
    )
    
    run = ProcessingRun(
        case_id=case_id,
        status="QUEUED",
        snapshot_hash=snapshot,
        config_version="1.0.0"
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    
    record_audit_event(
        db=db,
        case_id=case_id,
        action_type="RUN_QUEUED",
        actor_id="reviewer",
        payload={"run_id": run.id, "snapshot_hash": snapshot}
    )

    # Dispatch to background worker
    background_tasks.add_task(process_run, run.id)

    return run

@router.post("/runs/{run_id}/retry", response_model=ProcessingRunResponse)
def retry_processing_run(
    run_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    run = db.query(ProcessingRun).filter(ProcessingRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Processing run not found")

    run.status = "QUEUED"
    run.error_message = None
    db.commit()
    db.refresh(run)

    record_audit_event(
        db=db,
        case_id=run.case_id,
        action_type="RUN_RETRIED",
        actor_id="reviewer",
        payload={"run_id": run.id}
    )

    background_tasks.add_task(process_run, run.id)
    return run

@router.get("/runs/{run_id}", response_model=ProcessingRunResponse)
def get_run(run_id: str, db: Session = Depends(get_db)):
    r = db.query(ProcessingRun).filter(ProcessingRun.id == run_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Processing run not found")
    return r

@router.get("/runs/{run_id}/fields", response_model=List[FieldResponse])
def get_run_fields(run_id: str, db: Session = Depends(get_db)):
    return db.query(Field).filter(Field.run_id == run_id).all()

@router.get("/runs/{run_id}/claims", response_model=List[ClaimResponse])
def get_run_claims(run_id: str, db: Session = Depends(get_db)):
    return db.query(Claim).filter(Claim.run_id == run_id).all()

@router.get("/runs/{run_id}/transactions", response_model=List[TransactionResponse])
def get_run_transactions(run_id: str, db: Session = Depends(get_db)):
    return db.query(Transaction).filter(Transaction.run_id == run_id).all()

@router.get("/runs/{run_id}/findings", response_model=List[FindingResponse])
def get_run_findings(run_id: str, db: Session = Depends(get_db)):
    return db.query(Finding).filter(Finding.run_id == run_id).all()

@router.get("/runs/{run_id}/coverage")
def get_run_coverage(run_id: str, db: Session = Depends(get_db)):
    checks = db.query(CheckExecution).filter(CheckExecution.run_id == run_id).all()
    return {
        "run_id": run_id,
        "total_checks": len(checks),
        "checks": [
            {
                "id": c.id,
                "check_id": c.check_id,
                "lifecycle_state": c.lifecycle_state,
                "applicability": c.applicability,
                "outcome": c.outcome,
                "assumptions": c.assumptions,
                "limitations": c.scoped_limitations
            }
            for c in checks
        ]
    }
