from decimal import Decimal
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.models.field import Field, Claim, Transaction
from backend.app.models.execution import ProcessingRun, CheckExecution
from backend.app.models.finding import Finding
from backend.app.financial.reconciliation import (
    to_decimal,
    match_salary_credits,
    reconcile_income_declaration
)

def propagate_field_correction(
    db: Session,
    field_id: str,
    new_value: str,
    actor_id: str = "reviewer"
) -> Dict[str, Any]:
    """
    Propagates a reviewer field correction to dependent claims and re-evaluates reconciliation checks.
    Preserves original extraction and historic audit logs.
    """
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        return {"status": "ERROR", "message": "Field not found"}

    numeric_val = None
    try:
        clean_num = new_value.replace(",", "").replace("$", "").replace("₹", "").replace("INR", "").strip()
        numeric_val = float(clean_num)
    except ValueError:
        pass

    dependent_claims_updated = 0
    run_id = field.run_id

    # Find claims that reference this field in supporting_field_ids
    all_claims = db.query(Claim).filter(Claim.run_id == run_id).all()
    for claim in all_claims:
        if field.id in (claim.supporting_field_ids or []):
            if numeric_val is not None:
                claim.amount = numeric_val
                dependent_claims_updated += 1

    db.commit()

    # Re-run reconciliation checks on updated claims
    txs = db.query(Transaction).filter(Transaction.run_id == run_id).all()
    salary_claims = db.query(Claim).filter(Claim.run_id == run_id, Claim.claim_type == "SALARY_CLAIM").all()
    app_claims = db.query(Claim).filter(Claim.run_id == run_id, Claim.claim_type == "APPLICATION_CLAIM").all()

    recon_res = match_salary_credits(salary_claims, txs)
    income_align = reconcile_income_declaration(app_claims, salary_claims)

    return {
        "status": "PROPAGATED",
        "field_id": field_id,
        "new_value": new_value,
        "new_numeric_value": numeric_val,
        "dependent_claims_updated": dependent_claims_updated,
        "salary_reconciliation_status": recon_res.get("status"),
        "income_alignment_status": income_align.get("status")
    }

def calculate_coverage_matrix(db: Session, run_id: str) -> Dict[str, Any]:
    """
    Calculates the lifecycle, applicability, outcome, and limitations coverage matrix.
    """
    checks = db.query(CheckExecution).filter(CheckExecution.run_id == run_id).all()
    
    total = len(checks)
    completed = sum(1 for c in checks if c.lifecycle_state == "COMPLETED")
    consistent = sum(1 for c in checks if c.outcome == "CONSISTENT")
    discrepancy = sum(1 for c in checks if c.outcome == "DISCREPANCY")
    possible_expl = sum(1 for c in checks if c.outcome == "POSSIBLE_EXPLANATION")

    coverage_pct = round((completed / max(total, 1)) * 100, 1)

    checks_detail = []
    for c in checks:
        checks_detail.append({
            "check_id": c.check_id,
            "lifecycle_state": c.lifecycle_state,
            "applicability": c.applicability,
            "outcome": c.outcome,
            "assumptions": c.assumptions or [],
            "parameters_used": c.parameters_used or {},
            "limitations": c.scoped_limitations or "Standard inspection bounds"
        })

    return {
        "run_id": run_id,
        "total_checks": total,
        "completed_checks": completed,
        "coverage_percentage": coverage_pct,
        "outcomes": {
            "consistent": consistent,
            "discrepancy": discrepancy,
            "possible_explanation": possible_expl
        },
        "checks": checks_detail,
        "uninspected_regions": [
            "Handwritten signatures and non-English text layers",
            "Third-party external banking APIs (unintegrated)"
        ]
    }

