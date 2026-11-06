import os
import uuid
import pytest
import numpy as np
import cv2
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal, Base, engine
from backend.app.models.case import Case, Document, Page
from backend.app.models.execution import ProcessingRun, CheckExecution, VisualObservation
from backend.app.forensics.visual_baseline import (
    analyze_sharpness_variance,
    analyze_contrast_edge_discontinuity,
    analyze_native_font_consistency,
    save_crop_derivative,
    compute_laplacian_variance,
    extract_pixel_crop
)
from backend.worker.local_runner import process_run

def test_extract_pixel_crop_and_laplacian():
    # Create synthetic test image 100x100
    img = np.zeros((100, 100), dtype=np.uint8)
    # Add high frequency noise in subregion
    img[20:50, 20:50] = np.random.randint(0, 255, (30, 30), dtype=np.uint8)
    
    crop = extract_pixel_crop(img, [0.2, 0.2, 0.5, 0.5])
    assert crop.shape == (30, 30)
    var = compute_laplacian_variance(crop)
    assert var > 100.0  # High variance due to random noise

def test_sharpness_variance_synthetic_anomaly(tmp_path):
    img_path = str(tmp_path / "test_synth_page.png")
    # Base image: smooth background with moderate texture
    base = np.full((300, 300), 200, dtype=np.uint8)
    # Target region: high-contrast checkerboard
    base[50:100, 50:100] = np.random.randint(0, 255, (50, 50), dtype=np.uint8)
    cv2.imwrite(img_path, base)

    target_bbox = [50/300, 50/300, 100/300, 100/300]
    context_bbox = [150/300, 150/300, 250/300, 250/300] # smooth region

    res = analyze_sharpness_variance(img_path, target_bbox, context_bbox)
    assert res["status"] == "COMPLETED"
    assert res["sharpness_ratio"] > 3.0
    assert res["is_anomaly"] is True

def test_contrast_edge_discontinuity_synthetic_halo(tmp_path):
    img_path = str(tmp_path / "test_edge_halo.png")
    base = np.full((200, 200), 255, dtype=np.uint8)
    # Spliced box with sharp black rectangular border
    cv2.rectangle(base, (40, 40), (120, 80), 0, thickness=2)
    base[42:78, 42:118] = 240 # Light gray interior
    cv2.imwrite(img_path, base)

    target_bbox = [40/200, 40/200, 80/200, 120/200]
    res = analyze_contrast_edge_discontinuity(img_path, target_bbox)
    assert res["status"] == "COMPLETED"
    assert res["border_gradient_mean"] > 100.0

def test_native_font_consistency_clean_packet():
    pdf_path = os.path.join("data", "fictional_packets", "LOAN-2026-TR01", "application_form.pdf")
    assert os.path.exists(pdf_path)
    res = analyze_native_font_consistency(pdf_path, 1)
    assert res["status"] == "COMPLETED"
    assert res["is_consistent"] is True
    assert len(res["anomalies"]) == 0

def test_save_crop_derivative_disk(tmp_path):
    img_path = str(tmp_path / "test_crop_source.png")
    base = np.full((150, 150, 3), 128, dtype=np.uint8)
    cv2.imwrite(img_path, base)

    crop_path = save_crop_derivative(img_path, [0.1, 0.1, 0.4, 0.4], crop_prefix="unit_test")
    assert crop_path is not None
    assert os.path.exists(crop_path)
    assert crop_path.endswith(".png")

def test_end_to_end_visual_forensics_pipeline():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    case_ref = f"LOAN-TEST-VISUAL-{uuid.uuid4().hex[:8]}"

    case = Case(
        reference_number=case_ref,
        applicant_name="Visual Forensic Test",
        status="UNDER_INVESTIGATION"
    )
    db.add(case)
    db.commit()
    db.refresh(case)

    # Use VA02 salary slip m1 (which has baseline displacement)
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

    # Verify CHK_VISUAL_FORENSIC_BASELINE check execution exists
    chk_visual = db.query(CheckExecution).filter(
        CheckExecution.run_id == run.id,
        CheckExecution.check_id == "CHK_VISUAL_FORENSIC_BASELINE"
    ).first()
    assert chk_visual is not None
    assert chk_visual.lifecycle_state == "COMPLETED"
    assert chk_visual.applicability == "APPLICABLE"

    # Verify VisualObservation records exist with crop_path
    obs_list = db.query(VisualObservation).filter(VisualObservation.run_id == run.id).all()
    assert len(obs_list) >= 1
    # Check that baseline anomaly has a saved crop
    baseline_obs = [o for o in obs_list if o.detector_name == "font_baseline"]
    assert len(baseline_obs) >= 1
    assert baseline_obs[0].crop_path is not None
    assert os.path.exists(baseline_obs[0].crop_path)

    db.close()

