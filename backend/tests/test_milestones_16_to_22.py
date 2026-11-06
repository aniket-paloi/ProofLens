"""
Tests for ProofLens Milestones 16 to 22:
- Milestone 16: Integrity timeline, hash chain tamper detection, and retained checkpoint verification
- Milestone 17: Blind evaluation suite and honest capability matrix
- Milestone 18: Packaging manifest and judge narrative verification
- Milestone 19: Advanced localization & document robustness checks
- Milestone 20: FraudSim synthetic manipulation laboratory (Feature F15)
- Milestone 21: What-if hypothetical investigation branching (Feature F16)
- Milestone 22: Reviewer feedback & disposition analytics (Feature F17)
"""

import os
import json
import uuid
import cv2
import numpy as np
from decimal import Decimal
import pytest
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal, Base, engine
from backend.app.core.audit import record_audit_event, verify_case_audit_chain
from backend.app.models.case import Case, Document, Page
from backend.app.models.finding import AuditEvent, Finding, ReviewAction
from backend.app.models.execution import ProcessingRun
from backend.app.models.field import Claim, Transaction

# Milestone 16
from backend.app.audit.verifier import generate_case_checkpoint, verify_retained_checkpoint

# Milestone 17
from backend.evaluation.eval_suite import run_blind_evaluation, generate_capability_matrix_markdown

# Milestone 19
from backend.app.forensics.robustness import assess_document_robustness

# Milestone 20
from backend.app.lab.fraudsim import list_lab_scenarios, generate_synthetic_specimen

# Milestone 21
from backend.app.simulation.what_if import run_what_if_simulation

# Milestone 22
from backend.app.analytics.feedback import get_reviewer_feedback_metrics


@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_audit_hash_chain_tamper_detection(db: Session):
    """Milestone 16: Test SHA-256 event chaining and verify tamper detection."""
    case_ref = f"LOAN-TEST-AUDIT-{uuid.uuid4().hex[:8]}"
    case = Case(reference_number=case_ref, applicant_name="Audit Applicant")
    db.add(case)
    db.commit()
    db.refresh(case)

    # Record 3 sequential events
    ev1 = record_audit_event(db, case.id, "CASE_CREATED", "admin", {"step": 1})
    ev2 = record_audit_event(db, case.id, "DOCUMENT_UPLOADED", "admin", {"filename": "app.pdf"})
    ev3 = record_audit_event(db, case.id, "RUN_STARTED", "system", {"run_id": "test-run"})

    assert ev1.sequence_number == 1
    assert ev2.sequence_number == 2
    assert ev3.sequence_number == 3
    assert ev2.previous_event_hash == ev1.current_event_hash
    assert ev3.previous_event_hash == ev2.current_event_hash

    # Verify clean chain
    is_valid, msg, count = verify_case_audit_chain(db, case.id)
    assert is_valid is True
    assert count == 3

    # Tamper with event 2 payload directly in DB
    ev2.payload_json = '{"filename":"tampered.pdf"}'
    db.commit()

    # Verification must detect tampering
    is_valid_tampered, msg_tampered, failed_seq = verify_case_audit_chain(db, case.id)
    assert is_valid_tampered is False
    assert failed_seq == 2
    assert "Payload tampering detected" in msg_tampered


def test_retained_checkpoint_generation_and_verification(db: Session):
    """Milestone 16: Test generation and offline zero-trust checkpoint verification."""
    case_ref = f"LOAN-TEST-CHECKPOINT-{uuid.uuid4().hex[:8]}"
    case = Case(reference_number=case_ref, applicant_name="Checkpoint Applicant")
    db.add(case)
    db.commit()
    db.refresh(case)

    record_audit_event(db, case.id, "CASE_CREATED", "reviewer_01", {"action": "init"})
    record_audit_event(db, case.id, "FINDING_REVIEWED", "reviewer_01", {"disposition": "CONFIRMED"})

    checkpoint = generate_case_checkpoint(db, case.id, note="Unit Test Checkpoint")
    assert checkpoint["verification_status"] == "CRYPTOGRAPHICALLY_VERIFIED"
    assert checkpoint["event_count"] == 2
    assert os.path.exists(checkpoint["file_path"])

    # Verify offline checkpoint against db
    is_valid, msg, details = verify_retained_checkpoint(checkpoint, db=db)
    assert is_valid is True
    assert details["tamper_detected"] is False
    assert details["verified_events"] == 2

    # Verify with invalid checkpoint hash fails
    tampered_chk = dict(checkpoint)
    tampered_chk["latest_event_hash"] = "0" * 64
    is_val_t, msg_t, details_t = verify_retained_checkpoint(tampered_chk, db=db)
    assert is_val_t is False
    assert details_t["tamper_detected"] is True


def test_blind_evaluation_and_capability_matrix():
    """Milestone 17: Test blind evaluation runner and capability matrix writer."""
    eval_res = run_blind_evaluation()
    assert "metrics" in eval_res
    assert "accuracy" in eval_res["metrics"]
    assert "f1_score" in eval_res["metrics"]
    assert "ablation_study" in eval_res

    # Test markdown generation
    out_path = generate_capability_matrix_markdown(eval_res, output_path="docs/capability_matrix_test.md")
    assert os.path.exists(out_path)
    with open(out_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Honest Capability Matrix" in content
    assert "Ablation Study" in content
    if os.path.exists(out_path):
        os.remove(out_path)


def test_packaging_and_judge_narrative_assets():
    """Milestone 18: Verify existence and completeness of packaging and judge narrative docs."""
    judge_doc = os.path.join("demo", "JUDGE_NARRATIVE.md")
    packaging_doc = "PACKAGING_MANIFEST.md"
    launcher_ps = "start_prooflens.ps1"
    launcher_bat = "run_prooflens.bat"

    assert os.path.exists(judge_doc), "JUDGE_NARRATIVE.md missing"
    assert os.path.exists(packaging_doc), "PACKAGING_MANIFEST.md missing"
    assert os.path.exists(launcher_ps), "start_prooflens.ps1 missing"
    assert os.path.exists(launcher_bat), "run_prooflens.bat missing"

    with open(judge_doc, "r", encoding="utf-8") as f:
        narrative = f.read()
    assert "5-Minute Judge Demo Narrative" in narrative
    assert "Dual-Crop Raster Inspector" in narrative
    assert "Split-Payroll Matching" in narrative


def test_document_robustness_assessment():
    """Milestone 19: Test document raster quality and skew robustness."""
    # Synthetic clean sharp image (white background with black text-like blocks)
    clean_img = np.ones((800, 600, 3), dtype=np.uint8) * 255
    cv2.putText(clean_img, "ProofLens Robustness Test", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
    res_clean = assess_document_robustness(clean_img)
    assert res_clean["is_evaluable"] is True
    assert res_clean["is_skew_tolerable"] is True
    assert res_clean["robustness_score"] > 0.5

    # Synthetic blurred image
    blurred_img = cv2.GaussianBlur(clean_img, (25, 25), 0)
    res_blur = assess_document_robustness(blurred_img)
    assert res_blur["is_evaluable"] is True
    assert res_blur["blur_quality"] in ["MODERATE_BLUR", "HEAVILY_BLURRED"]


def test_fraudsim_synthetic_specimen_generation():
    """Milestone 20: Test FraudSim laboratory specimen creation in isolated sandbox."""
    scenarios = list_lab_scenarios()
    assert len(scenarios) >= 3

    # Test salary slip inflation synthesis
    specimen = generate_synthetic_specimen("SCN_SALARY_INFLATION", {"original_salary": 50000, "tampered_salary": 90000})
    assert specimen["status"] == "SPECIMEN_SYNTHESIZED"
    assert specimen["isolated"] is True
    assert specimen["ground_truth"]["altered_value"] == 90000.0
    assert os.path.exists(specimen["artifact_path"])

    # Test ledger shift synthesis
    spec_ledger = generate_synthetic_specimen("SCN_LEDGER_SHIFT", {"original_balance": 100000, "shift_amount": 25000})
    assert spec_ledger["ground_truth"]["unreconciled_discrepancy"] == 25000.0


def test_what_if_hypothetical_simulation(db: Session):
    """Milestone 21: Test what-if counterfactual branching without database mutation."""
    case_ref = f"LOAN-TEST-WHATIF-{uuid.uuid4().hex[:8]}"
    case = Case(reference_number=case_ref, applicant_name="Simulation Applicant")
    db.add(case)
    db.commit()
    db.refresh(case)

    doc = Document(
        case_id=case.id, filename="bank_statement.pdf", mime_type="application/pdf",
        file_size_bytes=2048, sha256_hash="hash_whatif_01", original_path="storage/originals/bank.pdf"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    page = Page(document_id=doc.id, page_number=1, width_pts=612.0, height_pts=792.0)
    db.add(page)
    db.commit()
    db.refresh(page)

    run = ProcessingRun(case_id=case.id, status="COMPLETED", snapshot_hash="snap_hash")
    db.add(run)
    db.commit()
    db.refresh(run)

    # Add a salary claim of 90,000 INR
    claim = Claim(
        run_id=run.id,
        claim_type="SALARY_CLAIM",
        subject="Simulation Applicant",
        basis="NET_SALARY",
        period_start="2026-05-01",
        period_end="2026-05-31",
        amount=Decimal("90000.00")
    )
    # Add a bank credit transaction of 60,000 INR (discrepancy of 30,000)
    tx = Transaction(
        run_id=run.id,
        page_id=page.id,
        transaction_date="2026-05-31",
        narration="Salary Credit Sim Tech",
        transaction_type="CREDIT",
        amount=Decimal("60000.00"),
        running_balance=Decimal("150000.00"),
        is_salary_candidate=1
    )
    db.add(claim)
    db.add(tx)
    db.commit()

    # Initial state has discrepancy (90,000 vs 60,000)
    # Test What-If: what if the applicant's declared net salary was actually 60,000?
    sim_res = run_what_if_simulation(db, case.id, {"simulated_salary": 60000.00})
    assert sim_res["is_isolated_hypothetical"] is True
    assert sim_res["simulated_outcomes"]["salary_reconciliation"]["all_matched"] is True

    # Confirm original claim in DB was not mutated
    db.refresh(claim)
    assert claim.amount == Decimal("90000.00")


def test_reviewer_feedback_analytics(db: Session):
    """Milestone 22: Test reviewer feedback metrics aggregation and non-retraining rule."""
    case_ref = f"LOAN-TEST-FEEDBACK-{uuid.uuid4().hex[:8]}"
    case = Case(reference_number=case_ref, applicant_name="Feedback Applicant")
    db.add(case)
    db.commit()
    db.refresh(case)

    run = ProcessingRun(case_id=case.id, status="COMPLETED", snapshot_hash="snap_fb")
    db.add(run)
    db.commit()
    db.refresh(run)

    f1 = Finding(
        case_id=case.id, run_id=run.id, title="Discrepancy 1", observation_type="CONTEXTUAL_MISMATCH",
        summary="Summary 1", reviewer_disposition="CONFIRMED"
    )
    f2 = Finding(
        case_id=case.id, run_id=run.id, title="Discrepancy 2", observation_type="VISUAL_ANOMALY",
        summary="Summary 2", reviewer_disposition="DISMISSED"
    )
    db.add_all([f1, f2])
    db.commit()

    metrics = get_reviewer_feedback_metrics(db)
    assert metrics["total_findings_recorded"] >= 2
    assert "disposition_distribution" in metrics
    assert "CONFIRMED" in metrics["disposition_distribution"]
    assert "governance_guarantee" in metrics
    assert "NEVER triggers automated online retraining" in metrics["governance_guarantee"]
