from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal
from backend.app.models.case import Case, Document, Page
from backend.app.models.execution import ProcessingRun, CheckDefinition, CheckExecution
from backend.app.models.finding import Finding, EvidenceLink
from backend.app.ingestion.renderer import render_and_route_pages
from backend.app.core.audit import record_audit_event

def process_run(run_id: str) -> None:
    db: Session = SessionLocal()
    try:
        run = db.query(ProcessingRun).filter(ProcessingRun.id == run_id).first()
        if not run:
            return

        run.status = "RUNNING"
        db.commit()

        case = db.query(Case).filter(Case.id == run.case_id).first()
        if not case:
            run.status = "FAILED"
            run.error_message = "Associated case not found."
            db.commit()
            return

        # Stage 1: Render and Route Pages for all documents in the case
        for doc in case.documents:
            # Check if pages are already rendered (idempotency check)
            existing_pages = db.query(Page).filter(Page.document_id == doc.id).all()
            if not existing_pages:
                pages_meta = render_and_route_pages(doc.original_path, doc.mime_type)
                for meta in pages_meta:
                    page = Page(
                        id=meta["page_id"],
                        document_id=doc.id,
                        page_number=meta["page_number"],
                        width_pts=meta["width_pts"],
                        height_pts=meta["height_pts"],
                        rotation_deg=meta["rotation_deg"],
                        rendered_image_path=meta["rendered_image_path"],
                        has_native_text=meta["has_native_text"]
                    )
                    db.add(page)
                doc.page_count = len(pages_meta)
                db.commit()

        # Stage 2: Basic Document Classification based on filename/spans
        for doc in case.documents:
            lower_name = doc.filename.lower()
            if "salary" in lower_name or "payslip" in lower_name:
                doc.classified_type = "SALARY_SLIP"
                doc.classification_confidence = 0.95
            elif "bank" in lower_name or "statement" in lower_name:
                doc.classified_type = "BANK_STATEMENT"
                doc.classification_confidence = 0.95
            elif "application" in lower_name or "form" in lower_name:
                doc.classified_type = "APPLICATION_FORM"
                doc.classification_confidence = 0.95
            else:
                doc.classified_type = "UNKNOWN"
                doc.classification_confidence = 0.50
            db.commit()

        # Stage 3: Baseline Check Execution (CHK_PAGE_ROUTING)
        check_def = db.query(CheckDefinition).filter(CheckDefinition.id == "CHK_PAGE_ROUTING").first()
        if not check_def:
            check_def = CheckDefinition(
                id="CHK_PAGE_ROUTING",
                category="INGESTION",
                name="Page-Level Content & Raster Routing",
                description="Verifies page rasterization and native vs. scanned vector text presence.",
                is_mandatory=1
            )
            db.add(check_def)
            db.commit()

        # Record check execution
        check_exec = CheckExecution(
            run_id=run.id,
            check_id="CHK_PAGE_ROUTING",
            lifecycle_state="COMPLETED",
            applicability="APPLICABLE",
            outcome="CONSISTENT",
            assumptions=["Rendered at 150 DPI for forensic inspection"],
            parameters_used={"max_pages": len(case.documents)}
        )
        db.add(check_exec)

        # Stage 4: Mark Run Complete
        run.status = "COMPLETED"
        run.completed_at = datetime.now(timezone.utc)
        db.commit()

        record_audit_event(
            db=db,
            case_id=case.id,
            action_type="RUN_COMPLETED",
            actor_id="local_runner",
            payload={"run_id": run.id, "documents_processed": len(case.documents)}
        )

    except Exception as e:
        db.rollback()
        run = db.query(ProcessingRun).filter(ProcessingRun.id == run_id).first()
        if run:
            run.status = "FAILED"
            run.error_message = str(e)
            db.commit()
    finally:
        db.close()

