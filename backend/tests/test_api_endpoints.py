import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import Base, engine

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

def test_health_live(client):
    res = client.get("/health/live")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.2.0"

def test_health_ready(client):
    res = client.get("/health/ready")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ready"
    assert "database" in data["details"]

def test_capabilities(client):
    res = client.get("/capabilities")
    assert res.status_code == 200
    data = res.json()
    assert data["capabilities"]["financial_reconciliation"] == "implemented"
    assert data["capabilities"]["integrity_hash_chain"] == "implemented"

def test_case_lifecycle_api(client):
    # 1. Create a case
    create_res = client.post("/api/cases", json={
        "reference_number": "LOAN-DEMO-2026",
        "applicant_name": "Aniket Paloi"
    })
    assert create_res.status_code == 201
    case_data = create_res.json()
    case_id = case_data["id"]
    assert case_data["reference_number"] == "LOAN-DEMO-2026"

    # 2. Get the case
    get_res = client.get(f"/api/cases/{case_id}")
    assert get_res.status_code == 200
    assert get_res.json()["applicant_name"] == "Aniket Paloi"

    # 3. Check audit trail
    audit_res = client.get(f"/api/cases/{case_id}/audit")
    assert audit_res.status_code == 200
    events = audit_res.json()
    assert len(events) >= 1
    assert events[0]["action_type"] == "CASE_CREATED"

    # 4. Verify cryptographic audit chain
    verify_res = client.post(f"/api/cases/{case_id}/audit/verify")
    assert verify_res.status_code == 200
    assert verify_res.json()["chain_valid"] is True
