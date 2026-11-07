import os
import hashlib
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Body
from fastapi.responses import FileResponse
from pydantic import BaseModel
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
from backend.app.financial.corrections import calculate_coverage_matrix
from backend.app.api.graph import build_case_claim_graph
from backend.app.agent.investigator import run_bounded_investigation, answer_case_question
from backend.app.reports.generator import generate_pdf_dossier
from backend.app.reports.manifest import generate_evidence_manifest
from backend.app.core.config import settings

router = APIRouter(tags=["Processing Runs & Intelligence"])

class QuestionRequest(BaseModel):
    question: str

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
    if getattr(settings, "IS_VERCEL", False):
        process_run(run.id)
        db.refresh(run)
    else:
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

    if getattr(settings, "IS_VERCEL", False):
        process_run(run.id)
        db.refresh(run)
    else:
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
    return calculate_coverage_matrix(db, run_id)

@router.get("/runs/{run_id}/graph")
def get_run_claim_graph(run_id: str, db: Session = Depends(get_db)):
    return build_case_claim_graph(db, run_id)

@router.post("/findings/{finding_id}/investigate")
def investigate_finding(
    finding_id: str,
    db: Session = Depends(get_db)
):
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    
    result = run_bounded_investigation(
        case_id=finding.case_id,
        run_id=finding.run_id,
        db=db,
        target_finding_id=finding_id
    )
    return result

@router.post("/runs/{run_id}/questions")
def ask_run_question(
    run_id: str,
    req: QuestionRequest,
    db: Session = Depends(get_db)
):
    return answer_case_question(run_id, req.question, db)

@router.post("/runs/{run_id}/reports")
def generate_run_reports(
    run_id: str,
    db: Session = Depends(get_db)
):
    run = db.query(ProcessingRun).filter(ProcessingRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Processing run not found")

    pdf_res = generate_pdf_dossier(db, run_id)
    manifest_res = generate_evidence_manifest(db, run_id)

    record_audit_event(
        db=db,
        case_id=run.case_id,
        action_type="REPORT_GENERATED",
        actor_id="reviewer",
        payload={
            "run_id": run.id,
            "pdf_report": pdf_res["filename"],
            "json_manifest": manifest_res["filename"]
        }
    )

    return {
        "status": "GENERATED",
        "run_id": run_id,
        "pdf_dossier": pdf_res["filename"],
        "json_manifest": manifest_res["filename"],
        "pdf_download_url": f"/api/reports/{pdf_res['filename']}",
        "manifest_download_url": f"/api/reports/{manifest_res['filename']}"
    }

@router.get("/reports/{filename}")
def download_report_file(filename: str):
    file_path = os.path.join(settings.REPORTS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    media_type = "application/pdf" if filename.endswith(".pdf") else "application/json"
    return FileResponse(file_path, media_type=media_type, filename=filename)
