import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.models.case import Case, Document, Page
from backend.app.models.execution import ProcessingRun, ToolExecution, CheckExecution
from backend.app.models.field import Field, Claim, Transaction
from backend.app.models.finding import Finding, EvidenceLink
from backend.app.agent.state import InvestigationSessionState, AgentToolCallRecord
from backend.app.agent.tools import (
    tool_inspect_crop,
    tool_crosscheck_text,
    tool_reconcile_balance,
    tool_match_salary_credit,
    tool_check_employer,
    tool_get_field_provenance,
    tool_suggest_disposition
)

def log_tool_execution(
    db: Session,
    run_id: str,
    tool_name: str,
    arguments: Dict[str, Any],
    result: Dict[str, Any],
    duration_ms: int
) -> ToolExecution:
    """Records an immutable tool execution entry in the database."""
    exec_record = ToolExecution(
        run_id=run_id,
        tool_name=tool_name,
        arguments=arguments,
        result=result,
        duration_ms=duration_ms
    )
    db.add(exec_record)
    db.commit()
    db.refresh(exec_record)
    return exec_record

def run_bounded_investigation(
    case_id: str,
    run_id: str,
    db: Session,
    target_finding_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes a bounded, evidence-driven investigation agent run with strict tool limits and state persistence.
    Adheres strictly to the Zero-Accusation Principle.
    """
    session = InvestigationSessionState(case_id=case_id, run_id=run_id)

    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        session.status = "FAILED"
        return {"status": "FAILED", "error": "Case not found"}

    # 1. Prompt Injection Defense & Text Layer Crosscheck (Tool 2)
    t0 = time.time()
    for doc in case.documents:
        pages = db.query(Page).filter(Page.document_id == doc.id).all()
        for page in pages:
            cross_res = tool_crosscheck_text(doc.original_path, page.page_number)
            if cross_res.get("injected_prompts"):
                session.quarantined = True
                session.quarantine_reason = f"Adversarial instruction payload detected on document {doc.filename} page {page.page_number}"
                session.status = "QUARANTINED"
                break
        if session.quarantined:
            break

    dur = int((time.time() - t0) * 1000)
    session.step_count += 1
    session.tool_history.append(AgentToolCallRecord(
        tool_name="tool_crosscheck_text",
        arguments={"case_id": case_id, "document_count": len(case.documents)},
        result={"quarantined": session.quarantined, "reason": session.quarantine_reason},
        timestamp=datetime.now(timezone.utc).isoformat(),
        duration_ms=dur
    ))
    log_tool_execution(
        db=db,
        run_id=run_id,
        tool_name="tool_crosscheck_text",
        arguments={"case_id": case_id, "document_count": len(case.documents)},
        result={"quarantined": session.quarantined, "reason": session.quarantine_reason},
        duration_ms=dur
    )

    if session.quarantined:
        session.recommended_disposition = "FURTHER_VERIFICATION_NEEDED"
        session.disposition_justification = f"Quarantined: {session.quarantine_reason}. Refusing automated execution."
        session.completed_at = datetime.now(timezone.utc).isoformat()
        return {
            "status": "QUARANTINED",
            "case_id": case_id,
            "run_id": run_id,
            "steps_executed": session.step_count,
            "quarantined": True,
            "quarantine_reason": session.quarantine_reason,
            "recommended_disposition": session.recommended_disposition,
            "disposition": session.recommended_disposition,
            "disposition_justification": session.disposition_justification,
            "justification": session.disposition_justification,
            "requires_human_sovereign_review": True,
            "session_state": session.__dict__
        }

    # 2. Arithmetic Ledger Verification (Tool 3)
    t0 = time.time()
    txs = db.query(Transaction).filter(Transaction.run_id == run_id).all()
    bal_res = tool_reconcile_balance(txs)
    dur = int((time.time() - t0) * 1000)
    session.step_count += 1
    session.tool_history.append(AgentToolCallRecord(
        tool_name="tool_reconcile_balance",
        arguments={"transaction_count": len(txs)},
        result={"is_reconciled": bal_res.get("is_reconciled"), "discrepancies_count": len(bal_res.get("discrepancies", []))},
        timestamp=datetime.now(timezone.utc).isoformat(),
        duration_ms=dur
    ))
    log_tool_execution(
        db=db,
        run_id=run_id,
        tool_name="tool_reconcile_balance",
        arguments={"transaction_count": len(txs)},
        result={"is_reconciled": bal_res.get("is_reconciled"), "discrepancies_count": len(bal_res.get("discrepancies", []))},
        duration_ms=dur
    )

    # 3. Salary Slip to Bank Credit Reconciliation (Tool 4)
    t0 = time.time()
    claims = db.query(Claim).filter(Claim.run_id == run_id, Claim.claim_type == "SALARY_CLAIM").all()
    sal_match = tool_match_salary_credit(claims, txs)
    dur = int((time.time() - t0) * 1000)
    session.step_count += 1
    session.tool_history.append(AgentToolCallRecord(
        tool_name="tool_match_salary_credit",
        arguments={"salary_claims_count": len(claims)},
        result={"all_matched": sal_match.get("all_matched"), "has_splits": sal_match.get("has_splits")},
        timestamp=datetime.now(timezone.utc).isoformat(),
        duration_ms=dur
    ))
    log_tool_execution(
        db=db,
        run_id=run_id,
        tool_name="tool_match_salary_credit",
        arguments={"salary_claims_count": len(claims)},
        result={"all_matched": sal_match.get("all_matched"), "has_splits": sal_match.get("has_splits")},
        duration_ms=dur
    )

    # 4. Employer Consistency Check (Tool 5)
    t0 = time.time()
    fields = db.query(Field).filter(Field.run_id == run_id).all()
    emp_res = tool_check_employer(fields, txs)
    dur = int((time.time() - t0) * 1000)
    session.step_count += 1
    session.tool_history.append(AgentToolCallRecord(
        tool_name="tool_check_employer",
        arguments={"field_count": len(fields)},
        result={"is_consistent": emp_res.get("is_consistent"), "mismatches_count": len(emp_res.get("mismatches", []))},
        timestamp=datetime.now(timezone.utc).isoformat(),
        duration_ms=dur
    ))
    log_tool_execution(
        db=db,
        run_id=run_id,
        tool_name="tool_check_employer",
        arguments={"field_count": len(fields)},
        result={"is_consistent": emp_res.get("is_consistent"), "mismatches_count": len(emp_res.get("mismatches", []))},
        duration_ms=dur
    )

    # 5. Document Lineage & Provenance Analysis (Tool 6)
    t0 = time.time()
    provenance_records = []
    for doc in case.documents:
        prov = tool_get_field_provenance(doc.classified_type or "UNKNOWN", doc.filename)
        provenance_records.append({"filename": doc.filename, "provenance": prov})
    dur = int((time.time() - t0) * 1000)
    session.step_count += 1
    session.tool_history.append(AgentToolCallRecord(
        tool_name="tool_get_field_provenance",
        arguments={"document_count": len(case.documents)},
        result={"provenance_records": provenance_records},
        timestamp=datetime.now(timezone.utc).isoformat(),
        duration_ms=dur
    ))
    log_tool_execution(
        db=db,
        run_id=run_id,
        tool_name="tool_get_field_provenance",
        arguments={"document_count": len(case.documents)},
        result={"provenance_records": provenance_records},
        duration_ms=dur
    )

    # 6. Synthesize Disposition Recommendation (Tool 7)
    t0 = time.time()
    all_findings = db.query(Finding).filter(Finding.run_id == run_id).all()
    findings_dicts = [
        {"title": f.title, "severity": f.severity, "observation_type": f.observation_type}
        for f in all_findings
    ]
    # Compute check coverage score
    checks = db.query(CheckExecution).filter(CheckExecution.run_id == run_id).all()
    completed_checks = [c for c in checks if c.lifecycle_state == "COMPLETED"]
    cov_score = len(completed_checks) / max(len(checks), 1)

    disp_res = tool_suggest_disposition(findings_dicts, cov_score)
    dur = int((time.time() - t0) * 1000)
    session.step_count += 1
    session.recommended_disposition = disp_res["recommended_disposition"]
    session.disposition_justification = disp_res["justification"]
    session.tool_history.append(AgentToolCallRecord(
        tool_name="tool_suggest_disposition",
        arguments={"findings_count": len(all_findings), "coverage_score": cov_score},
        result=disp_res,
        timestamp=datetime.now(timezone.utc).isoformat(),
        duration_ms=dur
    ))
    log_tool_execution(
        db=db,
        run_id=run_id,
        tool_name="tool_suggest_disposition",
        arguments={"findings_count": len(all_findings), "coverage_score": cov_score},
        result=disp_res,
        duration_ms=dur
    )

    session.status = "COMPLETED"
    session.completed_at = datetime.now(timezone.utc).isoformat()

    return {
        "status": "COMPLETED",
        "case_id": case_id,
        "run_id": run_id,
        "steps_executed": session.step_count,
        "quarantined": session.quarantined,
        "recommended_disposition": session.recommended_disposition,
        "disposition_justification": session.disposition_justification,
        "requires_human_sovereign_review": True,
        "tools_executed": [t.tool_name for t in session.tool_history]
    }

def answer_case_question(
    run_id: str,
    question: str,
    db: Session
) -> Dict[str, Any]:
    """
    Evidence-grounded case Q&A bounded strictly to extracted database facts and findings.
    Never hallucinates or goes beyond extracted fields.
    """
    run = db.query(ProcessingRun).filter(ProcessingRun.id == run_id).first()
    if not run:
        return {"answer": "Processing run not found.", "grounded_evidence": []}

    q_lower = question.lower()
    fields = db.query(Field).filter(Field.run_id == run_id).all()
    findings = db.query(Finding).filter(Finding.run_id == run_id).all()
    claims = db.query(Claim).filter(Claim.run_id == run_id).all()

    evidence_cited = []

    if "salary" in q_lower or "net" in q_lower or "gross" in q_lower or "income" in q_lower:
        salary_fields = [f for f in fields if "salary" in f.field_name.lower()]
        for sf in salary_fields:
            evidence_cited.append({
                "source": sf.field_name,
                "value": sf.normalized_value or sf.raw_value,
                "confidence": sf.extraction_score
            })
        ans = f"Extracted salary information across submitted documents: " + ", ".join(
            f"{e['source']} = {e['value']}" for e in evidence_cited
        )
        return {"question": question, "answer": ans, "grounded_evidence": evidence_cited}

    if "employer" in q_lower or "company" in q_lower or "work" in q_lower:
        emp_fields = [f for f in fields if "employer" in f.field_name.lower()]
        for ef in emp_fields:
            evidence_cited.append({
                "source": ef.field_name,
                "value": ef.raw_value
            })
        ans = "Employer references found: " + ", ".join(f"{e['source']} = {e['value']}" for e in evidence_cited)
        return {"question": question, "answer": ans, "grounded_evidence": evidence_cited}

    if "finding" in q_lower or "discrepancy" in q_lower or "issue" in q_lower or "anomaly" in q_lower:
        for f in findings:
            evidence_cited.append({
                "title": f.title,
                "severity": f.severity,
                "summary": f.summary
            })
        ans = f"Case has {len(findings)} recorded finding(s): " + "; ".join(f"[{f.severity}] {f.title}" for f in findings)
        return {"question": question, "answer": ans, "grounded_evidence": evidence_cited}

    # Default bounded response
    return {
        "question": question,
        "answer": f"Case analysis contains {len(fields)} extracted fields, {len(claims)} typed claims, and {len(findings)} findings.",
        "grounded_evidence": [{"total_fields": len(fields), "total_findings": len(findings)}]
    }
