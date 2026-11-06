import os
import uuid
from typing import List
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.audit import record_audit_event
from backend.app.models.case import Case, Document, Page
from backend.app.schemas.case import CaseCreate, CaseResponse, DocumentResponse, PageResponse
from backend.app.ingestion.validator import validate_and_inspect_document, DocumentValidationError

router = APIRouter(prefix="/cases", tags=["Cases & Ingestion"])

@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(case_in: CaseCreate, db: Session = Depends(get_db)):
    existing = db.query(Case).filter(Case.reference_number == case_in.reference_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Case with reference number '{case_in.reference_number}' already exists."
        )
    
    new_case = Case(
        reference_number=case_in.reference_number,
        applicant_name=case_in.applicant_name,
        status="ACTIVE"
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    
    record_audit_event(
        db=db,
        case_id=new_case.id,
        action_type="CASE_CREATED",
        actor_id="reviewer",
        payload={
            "case_id": new_case.id,
            "reference_number": new_case.reference_number,
            "applicant_name": new_case.applicant_name
        }
    )
    return new_case

@router.get("", response_model=List[CaseResponse])
def list_cases(db: Session = Depends(get_db)):
    return db.query(Case).order_by(Case.created_at.desc()).all()

@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: str, db: Session = Depends(get_db)):
    c = db.query(Case).filter(Case.id == case_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
    return c

@router.post("/{case_id}/documents", response_model=List[DocumentResponse], status_code=status.HTTP_201_CREATED)
async def upload_documents(
    case_id: str,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    uploaded_docs: List[Document] = []

    for file in files:
        try:
            file_bytes = await file.read()
            validated_meta = validate_and_inspect_document(file_bytes, file.filename or "unnamed_document")
        except DocumentValidationError as ve:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"error_code": ve.code, "message": ve.message, "filename": file.filename}
            )

        # Generate unique storage filename to preserve original bytes
        doc_id = str(uuid.uuid4())
        ext = Path(file.filename or "").suffix.lower()
        if not ext:
            ext = ".pdf" if validated_meta["mime_type"] == "application/pdf" else ".png"

        server_filename = f"{doc_id}{ext}"
        original_dest = settings.ORIGINALS_DIR / server_filename
        with open(original_dest, "wb") as f_out:
            f_out.write(file_bytes)

        doc = Document(
            id=doc_id,
            case_id=case.id,
            filename=file.filename or "document",
            mime_type=validated_meta["mime_type"],
            file_size_bytes=validated_meta["file_size_bytes"],
            sha256_hash=validated_meta["sha256_hash"],
            original_path=str(original_dest),
            classified_type="UNKNOWN",
            page_count=validated_meta["page_count"]
        )
        db.add(doc)
        uploaded_docs.append(doc)

        record_audit_event(
            db=db,
            case_id=case.id,
            action_type="DOCUMENT_UPLOADED",
            actor_id="reviewer",
            payload={
                "document_id": doc.id,
                "filename": doc.filename,
                "sha256_hash": doc.sha256_hash,
                "file_size_bytes": doc.file_size_bytes
            }
        )

    db.commit()
    for d in uploaded_docs:
        db.refresh(d)
    return uploaded_docs

@router.get("/{case_id}/documents", response_model=List[DocumentResponse])
def list_case_documents(case_id: str, db: Session = Depends(get_db)):
    c = db.query(Case).filter(Case.id == case_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
    return c.documents

@router.get("/{case_id}/timeline")
def get_case_timeline(case_id: str, db: Session = Depends(get_db)):
    from backend.app.core.audit import verify_case_audit_chain
    from backend.app.models.finding import AuditEvent
    c = db.query(Case).filter(Case.id == case_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
    events = (
        db.query(AuditEvent)
        .filter(AuditEvent.case_id == case_id)
        .order_by(AuditEvent.sequence_number.asc())
        .all()
    )
    is_valid, reason, count = verify_case_audit_chain(db, case_id)
    return {
        "case_id": case_id,
        "is_chain_valid": is_valid,
        "verification_status": "VERIFIED" if is_valid else "TAMPER_DETECTED",
        "verification_message": reason,
        "total_events": count,
        "timeline": [
            {
                "id": ev.id,
                "sequence_number": ev.sequence_number,
                "action_type": ev.action_type,
                "actor_id": ev.actor_id,
                "payload": ev.payload_json,
                "previous_event_hash": ev.previous_event_hash,
                "current_event_hash": ev.current_event_hash,
                "created_at": ev.created_at.isoformat() if ev.created_at else None
            }
            for ev in events
        ]
    }

@router.post("/{case_id}/checkpoint")
def create_checkpoint(case_id: str, db: Session = Depends(get_db)):
    from backend.app.audit.verifier import generate_case_checkpoint
    try:
        return generate_case_checkpoint(db=db, case_id=case_id)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@router.post("/{case_id}/verify-checkpoint")
def verify_checkpoint_endpoint(case_id: str, checkpoint_payload: dict, db: Session = Depends(get_db)):
    from backend.app.audit.verifier import verify_retained_checkpoint
    is_valid, msg, details = verify_retained_checkpoint(checkpoint_payload, db=db)
    return {
        "case_id": case_id,
        "is_valid": is_valid,
        "message": msg,
        "details": details
    }

# Document page serving router (registered directly or under /documents)
page_router = APIRouter(prefix="/documents", tags=["Document Derivatives"])

@page_router.get("/{document_id}/pages/{page_number}/image")
def get_page_image(document_id: str, page_number: int, db: Session = Depends(get_db)):
    page = (
        db.query(Page)
        .filter(Page.document_id == document_id, Page.page_number == page_number)
        .first()
    )
    if not page or not page.rendered_image_path or not os.path.exists(page.rendered_image_path):
        raise HTTPException(status_code=404, detail="Page render derivative not found")

    return FileResponse(page.rendered_image_path, media_type="image/png")
