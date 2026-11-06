import os
import uuid
import pytest
from decimal import Decimal
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal, Base, engine
from backend.app.models.case import Case, Document
from backend.app.models.execution import ProcessingRun, CheckExecution
from backend.app.models.field import Claim, Transaction, Field
from backend.app.models.finding import Finding, EvidenceLink
from backend.app.financial.reconciliation import (
    reconcile_bank_statement_balances,
    match_salary_credits,
    reconcile_income_declaration,
    check_employer_consistency,
    to_decimal
)
from backend.app.parsers.bank_parser import parse_bank_statement_document
from backend.worker.local_runner import process_run

def test_to_decimal_precision():
    assert to_decimal(105000) == Decimal("105000.00")
    assert to_decimal("105,000.50") == Decimal("105000.50")
    assert to_decimal("₹ 78,000.00") == Decimal("78000.00")
    assert to_decimal(None) == Decimal("0.00")

def test_bank_statement_balance_reconciliation_clean():
    pdf_path = os.path.join("data", "fictional_packets", "LOAN-2026-TR01", "bank_statement_3mo.pdf")
    parsed = parse_bank_statement_document(pdf_path)
    res = reconcile_bank_statement_balances(parsed["transactions"])
    assert res["is_reconciled"] is True
    assert len(res["discrepancies"]) == 0
    assert res["status"] == "RECONCILED"

def test_bank_statement_balance_reconciliation_failure():
    pdf_path = os.path.join("data", "fictional_packets", "LOAN-2026-TE03", "bank_statement_3mo.pdf")
    parsed = parse_bank_statement_document(pdf_path)
    res = reconcile_bank_statement_balances(parsed["transactions"])
    assert res["is_reconciled"] is False
    assert len(res["discrepancies"]) >= 1
    disc = res["discrepancies"][0]
    assert disc["delta"] == pytest.approx(50000.0, abs=1.0)
    assert disc["date"] == "01-JUN-2026"
    assert "ADANI PORTS" in disc["narration"]

def test_salary_credit_matcher_exact():
    pdf_path = os.path.join("data", "fictional_packets", "LOAN-2026-TR01", "bank_statement_3mo.pdf")
    parsed = parse_bank_statement_document(pdf_path)
    # TR01 has net salary of 95,000
    claims = [
        Claim(id="c1", basis="NET_SALARY", amount=95000.0, period_start="2026-04-01"),
        Claim(id="c2", basis="NET_SALARY", amount=95000.0, period_start="2026-05-01"),
        Claim(id="c3", basis="NET_SALARY", amount=95000.0, period_start="2026-06-01"),
    ]
    res = match_salary_credits(claims, parsed["transactions"])
    assert res["all_matched"] is True
    assert res["has_splits"] is False
    assert len(res["results"]) == 3
    for r in res["results"]:
        assert r["match_status"] == "EXACT_MATCH"
        assert r["matched_type"] == "SINGLE"
        assert r["variance"] == 0.0

def test_salary_credit_matcher_split_payroll():
    pdf_path = os.path.join("data", "fictional_packets", "LOAN-2026-TR03", "bank_statement_3mo.pdf")
    parsed = parse_bank_statement_document(pdf_path)
    # TR03 has net salary of 88,000 (split into 55k + 33k)
    claims = [
        Claim(id="c1", basis="NET_SALARY", amount=88000.0, period_start="2026-04-01"),
        Claim(id="c2", basis="NET_SALARY", amount=88000.0, period_start="2026-05-01"),
        Claim(id="c3", basis="NET_SALARY", amount=88000.0, period_start="2026-06-01"),
    ]
    res = match_salary_credits(claims, parsed["transactions"])
    assert res["all_matched"] is True
    assert res["has_splits"] is True
    assert len(res["results"]) == 3
    for r in res["results"]:
        assert r["match_status"] == "SPLIT_MATCH"
        assert r["matched_type"] == "MULTI_TRANSACTION"
        assert len(r["credits"]) == 2
        total_split = sum(c["amount"] for c in r["credits"])
        assert total_split == pytest.approx(88000.0, abs=0.1)

def test_salary_inflation_mismatch():
    pdf_path = os.path.join("data", "fictional_packets", "LOAN-2026-TR04", "bank_statement_3mo.pdf")
    parsed = parse_bank_statement_document(pdf_path)
    # TR04 declares net salary 76,000, but bank credits are only 45,000
    claims = [
        Claim(id="c1", basis="NET_SALARY", amount=76000.0, period_start="2026-04-01")
    ]
    res = match_salary_credits(claims, parsed["transactions"])
    assert res["all_matched"] is False
    assert res["results"][0]["match_status"] == "UNMATCHED_DISCREPANCY"
    assert res["results"][0]["variance"] == pytest.approx(31000.0, abs=0.1)

def test_employer_consistency_mismatch():
    fields_mismatch = [
        Field(field_name="employer_name", raw_value="Wipro Enterprises Ltd"),
        Field(field_name="employer_name", raw_value="Alpha Logistics Pvt Ltd")
    ]
    res = check_employer_consistency(fields_mismatch, [])
    assert res["is_consistent"] is False
    assert len(res["mismatches"]) == 1
    assert res["mismatches"][0]["declared"] == "Wipro Enterprises Ltd"
    assert res["mismatches"][0]["found"] == "Alpha Logistics Pvt Ltd"

    fields_clean = [
        Field(field_name="employer_name", raw_value="Tata Consultancy Services Ltd"),
        Field(field_name="employer_name", raw_value="Tata Consultancy Services Limited")
    ]
    res_clean = check_employer_consistency(fields_clean, [])
    assert res_clean["is_consistent"] is True
    assert len(res_clean["mismatches"]) == 0

def test_end_to_end_split_payroll_pipeline():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    case_ref = f"LOAN-TEST-SPLIT-{uuid.uuid4().hex[:8]}"
    
    case = Case(
        reference_number=case_ref,
        applicant_name="Rahul Verma",
        status="UNDER_INVESTIGATION"
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    
    # Upload TR03 packet docs (app form, payslip m1, bank statement)
    files_to_add = [
        ("application_form.pdf", "application/pdf"),
        ("salary_slip_m1.pdf", "application/pdf"),
        ("bank_statement_3mo.pdf", "application/pdf")
    ]
    import hashlib
    combined_hash = ""
    for filename, mime in files_to_add:
        pdf_path = os.path.join("data", "fictional_packets", "LOAN-2026-TR03", filename)
        with open(pdf_path, "rb") as f:
            b = f.read()
        h = hashlib.sha256(b).hexdigest()
        combined_hash += h
        doc = Document(
            case_id=case.id,
            filename=filename,
            mime_type=mime,
            sha256_hash=h,
            file_size_bytes=len(b),
            original_path=pdf_path
        )
        db.add(doc)
    db.commit()
    
    run = ProcessingRun(
        case_id=case.id,
        status="QUEUED",
        snapshot_hash=hashlib.sha256(combined_hash.encode()).hexdigest()
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    
    process_run(run.id)
    
    db.refresh(run)
    assert run.status == "COMPLETED"
    
    # Check that Candidate Multi-Transaction Split Payroll Match was found
    findings = db.query(Finding).filter(Finding.run_id == run.id).all()
    split_findings = [f for f in findings if "Split Payroll" in f.title]
    assert len(split_findings) >= 1
    sf = split_findings[0]
    assert sf.severity == "INFO"
    assert "split payroll structure" in sf.summary
    assert "88,000.00 INR" in sf.summary
    
    # Check CheckExecution outcomes
    chk_bal = db.query(CheckExecution).filter(
        CheckExecution.run_id == run.id,
        CheckExecution.check_id == "CHK_BALANCE_INTEGRITY"
    ).first()
    assert chk_bal is not None
    assert chk_bal.outcome == "CONSISTENT"
    
    chk_salary = db.query(CheckExecution).filter(
        CheckExecution.run_id == run.id,
        CheckExecution.check_id == "CHK_SALARY_CREDIT_RECON"
    ).first()
    assert chk_salary is not None
    assert chk_salary.outcome == "POSSIBLE_EXPLANATION"
    
    db.close()
