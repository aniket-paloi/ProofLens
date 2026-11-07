import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.database import Base, set_sqlite_pragma
from backend.app.models.case import Case, Document, Page
from backend.app.models.execution import ProcessingRun, CheckDefinition, CheckExecution
from backend.app.models.field import Field, Claim, Transaction
from backend.app.models.finding import Finding, EvidenceLink, ReviewAction, AuditEvent
from backend.app.core.audit import record_audit_event, verify_case_audit_chain

TEST_DB_URL = "sqlite:///./test_prooflens.db"

@pytest.fixture(scope="module")
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("./test_prooflens.db"):
        os.remove("./test_prooflens.db")

def test_case_creation_and_audit(db_session):
    # 1. Create Case
    test_case = Case(
        reference_number="TEST-LOAN-001",
        applicant_name="Aniket Paloi",
        status="ACTIVE"
    )
    db_session.add(test_case)
    db_session.commit()
    db_session.refresh(test_case)

    assert test_case.id is not None
    assert test_case.reference_number == "TEST-LOAN-001"

    # 2. Add Audit Event
    ev1 = record_audit_event(
        db=db_session,
        case_id=test_case.id,
        action_type="CASE_CREATED",
        actor_id="test_runner",
        payload={"ref": "TEST-LOAN-001"}
    )
    assert ev1.sequence_number == 1
    assert ev1.previous_event_hash == "0" * 64

    # 3. Add Document
    doc = Document(
        case_id=test_case.id,
        filename="salary_slip_jan.pdf",
        mime_type="application/pdf",
        file_size_bytes=10240,
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        original_path="storage/originals/salary_slip_jan.pdf",
        classified_type="SALARY_SLIP",
        classification_confidence=0.98,
        page_count=1
    )
    db_session.add(doc)
    db_session.commit()

    # 4. Add Page
    page = Page(
        document_id=doc.id,
        page_number=1,
        width_pts=595.0,
        height_pts=842.0,
        has_native_text=1
    )
    db_session.add(page)
    db_session.commit()

    # 5. Add Run & Field with Geometry
    run = ProcessingRun(
        case_id=test_case.id,
        status="COMPLETED",
        snapshot_hash="dummy_snapshot_hash"
    )
    db_session.add(run)
    db_session.commit()

    field = Field(
        run_id=run.id,
        page_id=page.id,
        field_name="net_salary",
        raw_value="₹ 75,000.00",
        normalized_value="75000.00",
        numeric_value=75000.00,
        currency="INR",
        bbox_normalized=[0.25, 0.40, 0.28, 0.65],
        extractor_name="pymupdf",
        extractor_version="1.25.0",
        extraction_score=0.99
    )
    db_session.add(field)
    db_session.commit()

    # 6. Second audit event
    ev2 = record_audit_event(
        db=db_session,
        case_id=test_case.id,
        action_type="DOCUMENT_PROCESSED",
        actor_id="worker",
        payload={"doc_id": doc.id, "fields_extracted": 1}
    )
    assert ev2.sequence_number == 2
    assert ev2.previous_event_hash == ev1.current_event_hash

    # 7. Verify cryptographic chain
    is_valid, msg, count = verify_case_audit_chain(db_session, test_case.id)
    assert is_valid is True
    assert count == 2

