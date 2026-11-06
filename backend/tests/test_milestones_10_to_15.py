import os
import uuid
import json
import pytest
import numpy as np
import cv2
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal, Base, engine
from backend.app.models.case import Case, Document, Page
from backend.app.models.execution import ProcessingRun, CheckExecution, ToolExecution, VisualObservation
from backend.app.models.field import Field, Claim, Transaction
from backend.app.models.finding import Finding
from backend.app.forensics.region_model import RegionClassifierAdapter
from backend.app.agent.investigator import run_bounded_investigation, answer_case_question
from backend.app.financial.corrections import propagate_field_correction, calculate_coverage_matrix
from backend.app.api.graph import build_case_claim_graph
from backend.app.reports.generator import generate_pdf_dossier
from backend.app.reports.manifest import generate_evidence_manifest
from backend.worker.local_runner import process_run

# -------------------------------------------------------------
# Milestone 10 & 11: Trained Region Model & Adapter
# -------------------------------------------------------------
def test_region_model_checkpoint_and_card_exist():
    ckpt_path = os.path.join("ml", "checkpoints", "mobilenet_v3_small_region.pt")
    card_path = os.path.join("ml", "MODEL_CARD.md")
    assert os.path.exists(ckpt_path), "Model checkpoint must exist"
    assert os.path.getsize(ckpt_path) > 1000000, "Checkpoint must be a full weights file (>1MB)"
    assert os.path.exists(card_path), "Model card must exist"
    
    with open(card_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "MobileNetV3 Small" in content
    assert "Limitations" in content

def test_region_model_inference_adapter(tmp_path):
    adapter = RegionClassifierAdapter()
    assert adapter.model is not None, "Model must load cleanly"

    dummy_crop_path = str(tmp_path / "crop_test.png")
    patch = np.full((100, 100, 3), 200, dtype=np.uint8)
    cv2.imwrite(dummy_crop_path, patch)

    pred = adapter.predict_crop(dummy_crop_path)
    assert pred["status"] == "COMPLETED"
    assert 0.0 <= pred["manipulation_probability"] <= 1.0
    assert isinstance(pred["is_anomaly"], bool)

# -------------------------------------------------------------
# Milestone 12: Bounded Investigation Agent & Tools
# -------------------------------------------------------------
def test_bounded_investigation_clean_case():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    case_ref = f"LOAN-TEST-AGENT-{uuid.uuid4().hex[:8]}"

    case = Case(reference_number=case_ref, applicant_name="Agent Case Test", status="ACTIVE")
    db.add(case)
    db.commit()
    db.refresh(case)

    pdf_path = os.path.join("data", "fictional_packets", "LOAN-2026-TR01", "application_form.pdf")
    with open(pdf_path, "rb") as f:
        b = f.read()
    import hashlib
    h = hashlib.sha256(b).hexdigest()

    doc = Document(
        case_id=case.id, filename="application_form.pdf", mime_type="application/pdf",
        sha256_hash=h, file_size_bytes=len(b), original_path=pdf_path
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    run = ProcessingRun(case_id=case.id, status="QUEUED", snapshot_hash=h)
    db.add(run)
    db.commit()
    db.refresh(run)

    process_run(run.id)

    # Run bounded agent investigation
    result = run_bounded_investigation(case_id=case.id, run_id=run.id, db=db)
    assert result["status"] == "COMPLETED"
    assert result["quarantined"] is False
    assert result["steps_executed"] >= 5
    assert result["recommended_disposition"] in ["CONFIRMED", "FURTHER_VERIFICATION_NEEDED"]
    assert len(result["tools_executed"]) >= 5

    # Verify tool executions persisted in DB
    tool_execs = db.query(ToolExecution).filter(ToolExecution.run_id == run.id).all()
    assert len(tool_execs) >= 5

    db.close()

def test_prompt_injection_defense_quarantine():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    case_ref = f"LOAN-TEST-QUARANTINE-{uuid.uuid4().hex[:8]}"

    case = Case(reference_number=case_ref, applicant_name="Adversarial Applicant", status="UNDER_INVESTIGATION")
    db.add(case)
    db.commit()
    db.refresh(case)

    # Load TR06 with prompt injection text layer
    pdf_path = os.path.join("data", "fictional_packets", "LOAN-2026-TR06", "application_form.pdf")
    with open(pdf_path, "rb") as f:
        b = f.read()
    import hashlib
    h = hashlib.sha256(b).hexdigest()

    doc = Document(
        case_id=case.id, filename="application_form.pdf", mime_type="application/pdf",
        sha256_hash=h, file_size_bytes=len(b), original_path=pdf_path
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    run = ProcessingRun(case_id=case.id, status="QUEUED", snapshot_hash=h)
    db.add(run)
    db.commit()
    db.refresh(run)

    process_run(run.id)

    # Run agent on adversarial document
    result = run_bounded_investigation(case_id=case.id, run_id=run.id, db=db)
    assert result["status"] == "QUARANTINED"
    assert result["quarantined"] is True
    assert result["recommended_disposition"] == "FURTHER_VERIFICATION_NEEDED"
    assert "Quarantined" in result["disposition_justification"]

    db.close()

def test_evidence_grounded_qa():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    r = db.query(ProcessingRun).filter(ProcessingRun.status == "COMPLETED").first()
    if r:
        q_ans = answer_case_question(r.id, "What is the applicant net salary?", db)
        assert "question" in q_ans
        assert "answer" in q_ans
        assert len(q_ans["grounded_evidence"]) >= 1
    db.close()

# -------------------------------------------------------------
# Milestone 13: Claim Connections, Coverage & Corrections
# -------------------------------------------------------------
def test_field_correction_propagation():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    field = db.query(Field).filter(Field.field_name == "net_salary").first()
    if field:
        claim = Claim(
            run_id=field.run_id,
            claim_type="SALARY_CLAIM",
            subject="Test Applicant",
            basis="NET_SALARY",
            amount=field.numeric_value or 80000.0,
            supporting_field_ids=[field.id]
        )
        db.add(claim)
        db.commit()

        # Propagate correction
        res = propagate_field_correction(db, field.id, "99,999.00", actor_id="sovereign_reviewer")
        assert res["status"] == "PROPAGATED"
        assert res["dependent_claims_updated"] >= 1
        db.refresh(claim)
        assert float(claim.amount) == pytest.approx(99999.0, abs=1.0)
    db.close()

def test_coverage_matrix():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    r = db.query(ProcessingRun).filter(ProcessingRun.status == "COMPLETED").first()
    if r:
        cov = calculate_coverage_matrix(db, r.id)
        assert cov["run_id"] == r.id
        assert cov["total_checks"] >= 5
        assert cov["coverage_percentage"] > 0.0
        assert len(cov["uninspected_regions"]) >= 1
    db.close()

# -------------------------------------------------------------
# Milestone 14: Claim Graph Read Projection
# -------------------------------------------------------------
def test_claim_graph_projection():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    r = db.query(ProcessingRun).filter(ProcessingRun.status == "COMPLETED").first()
    if r:
        graph = build_case_claim_graph(db, r.id)
        assert len(graph["nodes"]) >= 3
        assert len(graph["edges"]) >= 2
        assert "provenance_summary" in graph
        assert "invariant_note" in graph["provenance_summary"]
    db.close()

# -------------------------------------------------------------
# Milestone 15: Dossier & Reproducibility Bundle
# -------------------------------------------------------------
def test_pdf_dossier_and_json_manifest_generation():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    r = db.query(ProcessingRun).filter(ProcessingRun.status == "COMPLETED").first()
    if r:
        pdf_res = generate_pdf_dossier(db, r.id)
        assert os.path.exists(pdf_res["report_path"])
        assert pdf_res["byte_size"] > 2000
        assert pdf_res["filename"].endswith(".pdf")

        man_res = generate_evidence_manifest(db, r.id)
        assert os.path.exists(man_res["manifest_path"])
        assert man_res["filename"].endswith(".json")
        assert "case" in man_res["manifest"]
        assert "documents" in man_res["manifest"]
        assert "audit_trail" in man_res["manifest"]
    db.close()

