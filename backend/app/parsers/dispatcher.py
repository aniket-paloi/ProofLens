import os
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.case import Document, Page
from backend.app.models.field import Field, Claim, Transaction
from .application_parser import parse_application_document
from .salary_parser import parse_salary_document
from .bank_parser import parse_bank_statement_document

def extract_document_entities(db: Session, run_id: str, document: Document) -> Dict[str, Any]:
    """
    Extracts fields, claims, and transactions from a document based on its classified type.
    Creates and attaches models to the given run_id.
    """
    doc_type = document.classified_type
    file_path = document.original_path

    if not os.path.exists(file_path):
        return {"fields_created": 0, "claims_created": 0, "transactions_created": 0}

    # Retrieve first page
    first_page = db.query(Page).filter(Page.document_id == document.id).order_by(Page.page_number).first()
    if not first_page:
        return {"fields_created": 0, "claims_created": 0, "transactions_created": 0}

    extracted_data = None
    if doc_type == "APPLICATION_FORM":
        extracted_data = parse_application_document(file_path)
    elif doc_type == "SALARY_SLIP":
        extracted_data = parse_salary_document(file_path)
    elif doc_type == "BANK_STATEMENT":
        extracted_data = parse_bank_statement_document(file_path)

    if not extracted_data:
        return {"fields_created": 0, "claims_created": 0, "transactions_created": 0}

    fields_map = {}
    created_fields_count = 0
    created_claims_count = 0
    created_tx_count = 0

    # 1. Persist Fields
    for f in extracted_data.get("fields", []):
        field_model = Field(
            run_id=run_id,
            page_id=first_page.id,
            field_name=f["field_name"],
            raw_value=f["raw_value"],
            normalized_value=f.get("normalized_value"),
            numeric_value=f.get("numeric_value"),
            currency=f.get("currency", "INR"),
            period_start=f.get("period_start"),
            period_end=f.get("period_end"),
            bbox_normalized=f["bbox_normalized"],
            bbox_original=f.get("bbox_original"),
            extractor_name=f.get("extractor_name", "pymupdf_rule"),
            extractor_version="1.0.0",
            extraction_score=f.get("extraction_score", 0.95),
            current_revision_num=1
        )
        db.add(field_model)
        db.flush()
        fields_map[f["field_name"]] = field_model.id
        created_fields_count += 1

    # 2. Persist Claims
    for c in extracted_data.get("claims", []):
        supp_name = c.get("supporting_field_name")
        supporting_ids = [fields_map[supp_name]] if supp_name and supp_name in fields_map else []

        claim_model = Claim(
            run_id=run_id,
            claim_type=c["claim_type"],
            subject=c["subject"],
            basis=c["basis"],
            amount=c.get("amount"),
            currency=c.get("currency", "INR"),
            period_start=c.get("period_start"),
            period_end=c.get("period_end"),
            status=c.get("status", "ASSERTED"),
            supporting_field_ids=supporting_ids
        )
        db.add(claim_model)
        created_claims_count += 1

    # 3. Persist Transactions (if Bank Statement)
    for tx in extracted_data.get("transactions", []):
        tx_model = Transaction(
            run_id=run_id,
            page_id=first_page.id,
            transaction_date=tx["transaction_date"],
            narration=tx["narration"],
            transaction_type=tx["transaction_type"],
            amount=tx["amount"],
            running_balance=tx.get("running_balance"),
            is_salary_candidate=tx.get("is_salary_candidate", 0),
            bbox_normalized=tx.get("bbox_normalized")
        )
        db.add(tx_model)
        created_tx_count += 1

    db.commit()

    return {
        "fields_created": created_fields_count,
        "claims_created": created_claims_count,
        "transactions_created": created_tx_count
    }

