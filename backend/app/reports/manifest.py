import os
import json
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.case import Case, Document, Page
from backend.app.models.execution import ProcessingRun, CheckExecution, VisualObservation
from backend.app.models.field import Field, Claim, Transaction
from backend.app.models.finding import Finding, AuditEvent
from backend.app.core.config import settings

def generate_evidence_manifest(db: Session, run_id: str) -> Dict[str, Any]:
    """
    Builds a complete, reproducible machine-readable JSON evidence manifest for a run.
    """
    run = db.query(ProcessingRun).filter(ProcessingRun.id == run_id).first()
    if not run:
        raise ValueError(f"Run {run_id} not found")

    case = run.case

    manifest = {
        "manifest_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case": {
            "id": case.id,
            "reference_number": case.reference_number,
            "applicant_name": case.applicant_name,
            "status": case.status,
            "created_at": case.created_at.isoformat() if case.created_at else None
        },
        "run": {
            "id": run.id,
            "status": run.status,
            "snapshot_hash": run.snapshot_hash,
            "config_version": run.config_version,
            "created_at": run.created_at.isoformat() if run.created_at else None,
            "completed_at": run.completed_at.isoformat() if run.completed_at else None
        },
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "mime_type": doc.mime_type,
                "sha256_hash": doc.sha256_hash,
                "file_size_bytes": doc.file_size_bytes,
                "classified_type": doc.classified_type,
                "classification_confidence": doc.classification_confidence,
                "page_count": len(doc.pages)
            }
            for doc in case.documents
        ],
        "fields": [
            {
                "id": f.id,
                "field_name": f.field_name,
                "raw_value": f.raw_value,
                "normalized_value": f.normalized_value,
                "numeric_value": float(f.numeric_value) if f.numeric_value else None,
                "currency": f.currency,
                "bbox_normalized": f.bbox_normalized,
                "extractor_name": f.extractor_name,
                "revision": f.current_revision_num
            }
            for f in db.query(Field).filter(Field.run_id == run_id).all()
        ],
        "claims": [
            {
                "id": c.id,
                "claim_type": c.claim_type,
                "basis": c.basis,
                "amount": float(c.amount) if c.amount else None,
                "currency": c.currency,
                "status": c.status,
                "period_start": c.period_start,
                "period_end": c.period_end
            }
            for c in db.query(Claim).filter(Claim.run_id == run_id).all()
        ],
        "checks": [
            {
                "check_id": chk.check_id,
                "lifecycle_state": chk.lifecycle_state,
                "applicability": chk.applicability,
                "outcome": chk.outcome,
                "assumptions": chk.assumptions,
                "parameters_used": chk.parameters_used
            }
            for chk in db.query(CheckExecution).filter(CheckExecution.run_id == run_id).all()
        ],
        "findings": [
            {
                "id": fnd.id,
                "title": fnd.title,
                "observation_type": fnd.observation_type,
                "severity": fnd.severity,
                "uncertainty": fnd.uncertainty,
                "summary": fnd.summary,
                "alternative_explanations": fnd.alternative_explanations,
                "next_recommended_checks": fnd.next_recommended_checks,
                "reviewer_disposition": fnd.reviewer_disposition
            }
            for fnd in db.query(Finding).filter(Finding.run_id == run_id).all()
        ],
        "audit_trail": [
            {
                "sequence_number": ev.sequence_number,
                "action_type": ev.action_type,
                "actor_id": ev.actor_id,
                "current_event_hash": ev.current_event_hash,
                "previous_event_hash": ev.previous_event_hash,
                "created_at": ev.created_at.isoformat() if ev.created_at else None
            }
            for ev in db.query(AuditEvent).filter(AuditEvent.case_id == case.id).order_by(AuditEvent.sequence_number.asc()).all()
        ]
    }

    # Save to storage/reports
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    manifest_filename = f"manifest_{run_id}.json"
    manifest_path = os.path.join(settings.REPORTS_DIR, manifest_filename)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return {
        "manifest_path": manifest_path,
        "filename": manifest_filename,
        "manifest": manifest
    }

