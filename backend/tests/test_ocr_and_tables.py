import os
import uuid
import pytest
from backend.app.core.database import Base, engine, SessionLocal
from backend.app.models.case import Case, Document, Page
from backend.app.models.field import Field, Claim, Transaction
from backend.app.models.execution import ProcessingRun, CheckExecution
from backend.app.parsers.application_parser import parse_application_document
from backend.app.parsers.salary_parser import parse_salary_document
from backend.app.parsers.bank_parser import parse_bank_statement_document
from backend.worker.local_runner import process_run

PACKET_DIR = os.path.abspath("data/fictional_packets/LOAN-2026-TR01")

def test_application_form_parser():
    app_pdf = os.path.join(PACKET_DIR, "application_form.pdf")
    assert os.path.exists(app_pdf), "LOAN-2026-TR01 application_form.pdf must exist"

    res = parse_application_document(app_pdf)
    assert res["page_number"] == 1
    assert len(res["fields"]) >= 4

    field_names = {f["field_name"]: f for f in res["fields"]}
    assert "applicant_name" in field_names
    assert "Rajesh K. Sharma" in field_names["applicant_name"]["raw_value"]
    assert "gross_salary" in field_names
    assert field_names["gross_salary"]["numeric_value"] == 120000.0
    assert "net_salary" in field_names
    assert field_names["net_salary"]["numeric_value"] == 95000.0

    # Invariant: Normalized bounding boxes [ymin, xmin, ymax, xmax] in [0.0, 1.0]
    for f in res["fields"]:
        bbox = f["bbox_normalized"]
        assert len(bbox) == 4
        ymin, xmin, ymax, xmax = bbox
        assert 0.0 <= ymin <= ymax <= 1.0
        assert 0.0 <= xmin <= xmax <= 1.0

    # Invariant: Typed claims generated
    claim_types = [c["claim_type"] for c in res["claims"]]
    assert "SALARY_CLAIM" in claim_types
    assert "IDENTITY_CLAIM" in claim_types

def test_salary_slip_parser():
    slip_pdf = os.path.join(PACKET_DIR, "salary_slip_m1.pdf")
    assert os.path.exists(slip_pdf), "LOAN-2026-TR01 salary_slip_m1.pdf must exist"

    res = parse_salary_document(slip_pdf)
    assert res["page_number"] == 1
    assert len(res["fields"]) >= 3

    field_names = {f["field_name"]: f for f in res["fields"]}
    assert "net_salary" in field_names
    assert field_names["net_salary"]["numeric_value"] == 95000.0
    assert "gross_salary" in field_names
    assert field_names["gross_salary"]["numeric_value"] == 120000.0

    # Verify period
    assert field_names["net_salary"]["period_start"] == "2026-04-01"
    assert field_names["net_salary"]["period_end"] == "2026-04-30"

    # Verify geometry
    for f in res["fields"]:
        bbox = f["bbox_normalized"]
        assert len(bbox) == 4
        ymin, xmin, ymax, xmax = bbox
        assert 0.0 <= ymin <= ymax <= 1.0

def test_bank_statement_parser():
    bank_pdf = os.path.join(PACKET_DIR, "bank_statement_3mo.pdf")
    assert os.path.exists(bank_pdf), "LOAN-2026-TR01 bank_statement_3mo.pdf must exist"

    res = parse_bank_statement_document(bank_pdf)
    assert len(res["transactions"]) >= 3

    # Check that salary candidate is identified
    salary_candidates = [tx for tx in res["transactions"] if tx["is_salary_candidate"] == 1]
    assert len(salary_candidates) >= 1
    assert salary_candidates[0]["amount"] == 95000.0
    assert salary_candidates[0]["transaction_type"] == "CREDIT"

    # Verify claims
    salary_claims = [c for c in res["claims"] if c["basis"] == "BANK_CREDIT"]
    assert len(salary_claims) >= 1
    assert salary_claims[0]["amount"] == 95000.0

def test_end_to_end_extraction_pipeline():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    unique_ref = f"LOAN-OCR-{uuid.uuid4().hex[:8]}"

    # 1. Create a Case
    case = Case(
        reference_number=unique_ref,
        applicant_name="Rajesh K. Sharma"
    )
    db.add(case)
    db.commit()
    db.refresh(case)

    # 2. Add Documents from LOAN-2026-TR01
    doc_app = Document(
        case_id=case.id,
        filename="application_form.pdf",
        mime_type="application/pdf",
        file_size_bytes=os.path.getsize(os.path.join(PACKET_DIR, "application_form.pdf")),
        sha256_hash=f"hash_app_{uuid.uuid4().hex[:6]}",
        original_path=os.path.join(PACKET_DIR, "application_form.pdf")
    )
    doc_slip = Document(
        case_id=case.id,
        filename="salary_slip_m1.pdf",
        mime_type="application/pdf",
        file_size_bytes=os.path.getsize(os.path.join(PACKET_DIR, "salary_slip_m1.pdf")),
        sha256_hash=f"hash_slip_{uuid.uuid4().hex[:6]}",
        original_path=os.path.join(PACKET_DIR, "salary_slip_m1.pdf")
    )
    doc_bank = Document(
        case_id=case.id,
        filename="bank_statement_3mo.pdf",
        mime_type="application/pdf",
        file_size_bytes=os.path.getsize(os.path.join(PACKET_DIR, "bank_statement_3mo.pdf")),
        sha256_hash=f"hash_bank_{uuid.uuid4().hex[:6]}",
        original_path=os.path.join(PACKET_DIR, "bank_statement_3mo.pdf")
    )
    db.add_all([doc_app, doc_slip, doc_bank])
    db.commit()

    # 3. Create Run
    run = ProcessingRun(
        case_id=case.id,
        status="QUEUED",
        snapshot_hash="dummy_snapshot",
        config_version="1.0.0"
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # 4. Execute Pipeline
    process_run(run.id)

    # 5. Verify database state
    db.refresh(run)
    assert run.status == "COMPLETED"

    fields = db.query(Field).filter(Field.run_id == run.id).all()
    assert len(fields) >= 8

    claims = db.query(Claim).filter(Claim.run_id == run.id).all()
    assert len(claims) >= 4

    txs = db.query(Transaction).filter(Transaction.run_id == run.id).all()
    assert len(txs) >= 3

    # Verify check execution
    chk = db.query(CheckExecution).filter(
        CheckExecution.run_id == run.id,
        CheckExecution.check_id == "CHK_SOURCE_EXTRACTION"
    ).first()
    assert chk is not None
    assert chk.outcome == "CONSISTENT"

    db.close()
