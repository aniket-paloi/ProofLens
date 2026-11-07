import os
import io
import pytest
import pymupdf
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import Base, engine, SessionLocal
from backend.app.models.case import Case, Document, Page
from backend.app.models.execution import ProcessingRun
from backend.worker.local_runner import process_run

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

def create_synthetic_pdf(text_pages: list[str]) -> bytes:
    doc = pymupdf.open()
    for text in text_pages:
        page = doc.new_page(width=595, height=842)
        if text:
            page.insert_text((50, 100), text, fontsize=12)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

def test_multi_document_upload_and_validation(client):
    # 1. Create a Case
    case_res = client.post("/api/cases", json={
        "reference_number": "LOAN-INGEST-001",
        "applicant_name": "Aniket Paloi"
    })
    assert case_res.status_code == 201
    case_id = case_res.json()["id"]

    # 2. Create synthetic PDFs: 1 salary slip, 1 bank statement
    salary_pdf = create_synthetic_pdf(["Acme Corp Salary Slip\nApplicant: Aniket Paloi\nNet Salary: 75,000 INR"])
    bank_pdf = create_synthetic_pdf(["State Bank Statement\nAccount: 123456789\nBalance: 150,000 INR"])

    # 3. Upload both documents
    files = [
        ("files", ("salary_slip_jan.pdf", salary_pdf, "application/pdf")),
        ("files", ("bank_statement_q1.pdf", bank_pdf, "application/pdf"))
    ]
    upload_res = client.post(f"/api/cases/{case_id}/documents", files=files)
    assert upload_res.status_code == 201
    docs = upload_res.json()
    assert len(docs) == 2
    assert docs[0]["filename"] == "salary_slip_jan.pdf"
    assert docs[0]["mime_type"] == "application/pdf"
    assert docs[0]["sha256_hash"] is not None

    # 4. Trigger Processing Run
    run_res = client.post(f"/api/cases/{case_id}/runs")
    assert run_res.status_code == 201
    run_id = run_res.json()["id"]

    # 5. Execute local runner
    process_run(run_id)

    # 6. Verify run status and page derivatives
    get_run = client.get(f"/api/runs/{run_id}")
    assert get_run.status_code == 200
    assert get_run.json()["status"] == "COMPLETED"

    # Verify pages were rendered
    db = SessionLocal()
    doc_ids = [d["id"] for d in docs]
    pages = db.query(Page).filter(Page.document_id.in_(doc_ids)).all()
    assert len(pages) == 2
    for p in pages:
        assert p.rendered_image_path is not None
        assert os.path.exists(p.rendered_image_path)
        assert p.has_native_text == 1  # Verified native text extracted
    db.close()

def test_mixed_page_routing(client):
    # Test a PDF with 1 native text page and 1 scanned/empty page
    mixed_pdf = create_synthetic_pdf([
        "Page 1 has plenty of searchable vector text extracted from native PDF streams.",
        ""  # Page 2 has no vector text (pure scanned/raster simulation)
    ])

    case_res = client.post("/api/cases", json={
        "reference_number": "LOAN-MIXED-002",
        "applicant_name": "Mixed Page Case"
    })
    case_id = case_res.json()["id"]

    upload_res = client.post(f"/api/cases/{case_id}/documents", files=[
        ("files", ("mixed_doc.pdf", mixed_pdf, "application/pdf"))
    ])
    assert upload_res.status_code == 201

    run_res = client.post(f"/api/cases/{case_id}/runs")
    run_id = run_res.json()["id"]
    process_run(run_id)

    db = SessionLocal()
    case_pages = (
        db.query(Page)
        .join(Document, Page.document_id == Document.id)
        .filter(Document.case_id == case_id)
        .order_by(Page.page_number.asc())
        .all()
    )
    assert len(case_pages) == 2
    assert case_pages[0].has_native_text == 1  # Page 1 routed to native parser
    assert case_pages[1].has_native_text == 0  # Page 2 routed to raster OCR parser
    db.close()

def test_invalid_upload_handling(client):
    case_res = client.post("/api/cases", json={
        "reference_number": "LOAN-ERR-003",
        "applicant_name": "Error Testing Case"
    })
    case_id = case_res.json()["id"]

    # 1. Non-PDF with spoofed extension
    fake_pdf = b"This is plain text with a .pdf extension"
    res1 = client.post(f"/api/cases/{case_id}/documents", files=[
        ("files", ("fake.pdf", fake_pdf, "application/pdf"))
    ])
    assert res1.status_code == 422
    assert res1.json()["detail"]["error_code"] == "UNSUPPORTED_MIME_TYPE"

    # 2. Corrupt PDF
    corrupt_pdf = b"%PDF-1.4\nCorrupt bytes that crash the parser"
    res2 = client.post(f"/api/cases/{case_id}/documents", files=[
        ("files", ("corrupt.pdf", corrupt_pdf, "application/pdf"))
    ])
    assert res2.status_code == 422
    assert res2.json()["detail"]["error_code"] == "CORRUPT_DOCUMENT"

def test_run_retry_idempotency(client):
    case_res = client.post("/api/cases", json={
        "reference_number": "LOAN-RETRY-004",
        "applicant_name": "Retry Test Case"
    })
    case_id = case_res.json()["id"]

    pdf_bytes = create_synthetic_pdf(["Idempotency Test Document Content"])
    client.post(f"/api/cases/{case_id}/documents", files=[
        ("files", ("doc.pdf", pdf_bytes, "application/pdf"))
    ])

    run_res = client.post(f"/api/cases/{case_id}/runs")
    run_id = run_res.json()["id"]

    # Run 1st time
    process_run(run_id)

    # Retry the run
    retry_res = client.post(f"/api/runs/{run_id}/retry")
    assert retry_res.status_code == 200
    process_run(run_id)

    # Verify no duplicated pages
    db = SessionLocal()
    pages = db.query(Page).join(Document).filter(Document.case_id == case_id).all()
    assert len(pages) == 1
    db.close()

