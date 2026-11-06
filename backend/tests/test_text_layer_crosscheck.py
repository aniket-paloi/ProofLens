import os
import uuid
import pytest
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal, Base, engine
from backend.app.models.case import Case, Document
from backend.app.models.execution import ProcessingRun, CheckExecution, VisualObservation
from backend.app.models.finding import Finding, EvidenceLink
from backend.app.parsers.crosscheck import (
    crosscheck_page_text_layers,
    crosscheck_document_text_layers
)
from backend.worker.local_runner import process_run

def test_crosscheck_clean_document():
    pdf_path = os.path.join("data", "fictional_packets", "LOAN-2026-TR01", "application_form.pdf")
    assert os.path.exists(pdf_path), "TR01 application form must exist"
    
    res = crosscheck_page_text_layers(pdf_path, 1)
    assert res["page_number"] == 1
    assert res["total_spans"] > 10
    assert res["is_consistent"] is True
    assert len(res["invisible_spans"]) == 0
    assert len(res["injected_prompts"]) == 0
    assert len(res["baseline_anomalies"]) == 0

def test_crosscheck_prompt_injection_detection():
    pdf_path = os.path.join("data", "fictional_packets", "LOAN-2026-TR06", "application_form.pdf")
    assert os.path.exists(pdf_path), "TR06 application form must exist"
    
    res = crosscheck_page_text_layers(pdf_path, 1)
    assert res["is_consistent"] is False
    assert len(res["invisible_spans"]) == 1
    assert res["invisible_spans"][0]["reason"] == "white_on_white"
    assert res["invisible_spans"][0]["color_rgb"] == [255, 255, 255]
    
    assert len(res["injected_prompts"]) == 1
    inj = res["injected_prompts"][0]
    assert inj["matched_keyword"] == "system prompt"
    assert "System Prompt Override" in inj["full_text"]
    
    bbox = inj["bbox_normalized"]
    assert len(bbox) == 4
    assert 0.0 <= bbox[0] <= bbox[2] <= 1.0
    assert 0.0 <= bbox[1] <= bbox[3] <= 1.0

def test_crosscheck_baseline_displacement_detection():
    tampered_pdf = os.path.join("data", "fictional_packets", "LOAN-2026-VA02", "salary_slip_m1.pdf")
    assert os.path.exists(tampered_pdf), "VA02 salary slip m1 must exist"
    
    res_tampered = crosscheck_page_text_layers(tampered_pdf, 1)
    assert res_tampered["is_consistent"] is False
    assert len(res_tampered["baseline_anomalies"]) >= 1
    
    anom = res_tampered["baseline_anomalies"][0]
    assert anom["text_left"] == "NET PAYABLE:"
    assert "92,000" in anom["text_right"]
    assert anom["baseline_delta_px"] == pytest.approx(3.5, abs=0.1)
    
    # Untampered month 2 in the same packet must be consistent
    clean_pdf = os.path.join("data", "fictional_packets", "LOAN-2026-VA02", "salary_slip_m2.pdf")
    assert os.path.exists(clean_pdf), "VA02 salary slip m2 must exist"
    res_clean = crosscheck_page_text_layers(clean_pdf, 1)
    assert len(res_clean["baseline_anomalies"]) == 0

def test_end_to_end_prompt_injection_pipeline():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    case_ref = f"LOAN-TEST-INJ-{uuid.uuid4().hex[:8]}"
    
    case = Case(
        reference_number=case_ref,
        applicant_name="Devendra Rathi",
        status="UNDER_INVESTIGATION"
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    
    pdf_path = os.path.join("data", "fictional_packets", "LOAN-2026-TR06", "application_form.pdf")
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()
    import hashlib
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    
    doc = Document(
        case_id=case.id,
        filename="application_form.pdf",
        mime_type="application/pdf",
        sha256_hash=sha256,
        file_size_bytes=len(file_bytes),
        original_path=pdf_path
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    run = ProcessingRun(
        case_id=case.id,
        status="QUEUED",
        snapshot_hash=sha256
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    
    process_run(run.id)
    
    db.refresh(run)
    assert run.status == "COMPLETED"
    
    findings = db.query(Finding).filter(Finding.run_id == run.id).all()
    assert len(findings) >= 1
    critical_findings = [f for f in findings if f.severity == "CRITICAL"]
    assert len(critical_findings) == 1
    
    crit = critical_findings[0]
    assert crit.observation_type == "TEXT_LAYER_DESYNC"
    assert "Adversarial Instruction" in crit.title
    assert "system prompt" in crit.summary
    
    ev_links = db.query(EvidenceLink).filter(EvidenceLink.finding_id == crit.id).all()
    assert len(ev_links) >= 1
    assert ev_links[0].entity_type == "PAGE"
    
    check_exec = db.query(CheckExecution).filter(
        CheckExecution.run_id == run.id,
        CheckExecution.check_id == "CHK_TEXT_LAYER_INTEGRITY"
    ).first()
    assert check_exec is not None
    assert check_exec.outcome == "DISCREPANCY"
    assert check_exec.parameters_used["prompt_injections_found"] == 1
    
    db.close()

def test_end_to_end_baseline_anomaly_pipeline():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    case_ref = f"LOAN-TEST-BASE-{uuid.uuid4().hex[:8]}"
    
    case = Case(
        reference_number=case_ref,
        applicant_name="Sunita Joshi",
        status="UNDER_INVESTIGATION"
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    
    pdf_path = os.path.join("data", "fictional_packets", "LOAN-2026-VA02", "salary_slip_m1.pdf")
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()
    import hashlib
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    
    doc = Document(
        case_id=case.id,
        filename="salary_slip_m1.pdf",
        mime_type="application/pdf",
        sha256_hash=sha256,
        file_size_bytes=len(file_bytes),
        original_path=pdf_path
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    run = ProcessingRun(
        case_id=case.id,
        status="QUEUED",
        snapshot_hash=sha256
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    
    process_run(run.id)
    
    db.refresh(run)
    assert run.status == "COMPLETED"
    
    # Check that VisualObservation was registered
    observations = db.query(VisualObservation).filter(VisualObservation.run_id == run.id).all()
    assert len(observations) >= 1
    obs = observations[0]
    assert obs.detector_name == "font_baseline"
    assert obs.measured_property == "vertical_baseline_displacement_px"
    assert obs.measured_value == pytest.approx(3.5, abs=0.1)
    
    # Check that Finding was registered
    findings = db.query(Finding).filter(Finding.run_id == run.id).all()
    baseline_findings = [f for f in findings if f.observation_type == "VISUAL_ANOMALY"]
    assert len(baseline_findings) >= 1
    bf = baseline_findings[0]
    assert bf.severity == "MEDIUM"
    assert "Baseline Displacement" in bf.title
    
    # Check execution status
    check_exec = db.query(CheckExecution).filter(
        CheckExecution.run_id == run.id,
        CheckExecution.check_id == "CHK_TEXT_LAYER_INTEGRITY"
    ).first()
    assert check_exec is not None
    assert check_exec.outcome == "DISCREPANCY"
    assert check_exec.parameters_used["baseline_anomalies_found"] >= 1
    
    db.close()
