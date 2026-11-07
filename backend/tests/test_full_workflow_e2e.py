import os
import io
import fitz
import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import Base, engine

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

def test_full_document_pipeline_e2e():
    with TestClient(app) as client:
        # 1. Create a Case
        ref_num = f"E2E-CASE-{os.urandom(4).hex().upper()}"
        res = client.post("/api/cases", json={
            "reference_number": ref_num,
            "applicant_name": "Aniket Paloi"
        })
        assert res.status_code == 201
        case_data = res.json()
        case_id = case_data["id"]
        assert case_data["reference_number"] == ref_num

        # 2. Upload Document
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 72), "Credit Application Form", fontsize=18)
        page.insert_text((50, 100), "Applicant: Aniket Paloi", fontsize=11)
        page.insert_text((50, 120), "Employer: Apex FinTech Labs Pvt Ltd", fontsize=11)
        page.insert_text((50, 140), "Monthly Gross Income: 90000.00", fontsize=11)
        page.insert_text((50, 160), "Net In-Hand Salary: 75000.00", fontsize=11)
        pdf_bytes = doc.tobytes()
        doc.close()

        files = [
            ("files", ("Application_Form.pdf", io.BytesIO(pdf_bytes), "application/pdf"))
        ]
        res_upload = client.post(f"/api/cases/{case_id}/documents", files=files)
        assert res_upload.status_code == 201
        docs = res_upload.json()
        assert len(docs) == 1
        doc_id = docs[0]["id"]
        assert docs[0]["filename"] == "Application_Form.pdf"
        assert docs[0]["sha256_hash"] is not None

        # 3. Test Document Download Endpoint
        res_dl = client.get(f"/api/documents/{doc_id}/download")
        assert res_dl.status_code == 200
        assert len(res_dl.content) == len(pdf_bytes)
        assert res_dl.headers["content-type"] == "application/pdf"

        # 4. Test Document Page Render Derivative Image
        res_page = client.get(f"/api/documents/{doc_id}/pages/1/image")
        assert res_page.status_code == 200
        assert res_page.headers["content-type"] == "image/png"
        assert len(res_page.content) > 100

        # 5. Trigger Processing Run
        res_run = client.post(f"/api/cases/{case_id}/runs")
        assert res_run.status_code == 201
        run_data = res_run.json()
        assert run_data["status"] in ["QUEUED", "RUNNING", "COMPLETED"]

        # 6. Verify Online Audit Checkpoint
        res_verify = client.post(f"/api/cases/{case_id}/audit/verify")
        assert res_verify.status_code == 200
        v_data = res_verify.json()
        assert v_data["chain_valid"] is True
        assert v_data["total_events"] >= 2  # CASE_CREATED, DOCUMENT_UPLOADED, RUN_QUEUED

        # 7. Generate Retained Checkpoint and Verify
        res_chk = client.post(f"/api/cases/{case_id}/checkpoint")
        assert res_chk.status_code == 200
        chk_payload = res_chk.json()
        assert "chain_digest" in chk_payload
        assert chk_payload["event_count"] >= 2
        assert chk_payload["verification_status"] == "CRYPTOGRAPHICALLY_VERIFIED"

        # 8. Test Checkpoint Verification Endpoint
        res_chk_verify = client.post(f"/api/cases/{case_id}/verify-checkpoint", json=chk_payload)
        assert res_chk_verify.status_code == 200
        assert res_chk_verify.json()["is_valid"] is True
