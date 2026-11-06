"""
ProofLens What-If Hypothetical Investigation Branching (Milestone 21 / Feature F16)
Allows reviewers to test counterfactual assertions (e.g. "What if salary was 75,000 instead of 45,000?")
in complete isolation from official case evidence, audit trails, and frozen reports.
"""

import uuid
from decimal import Decimal
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.models.case import Case
from backend.app.models.execution import ProcessingRun
from backend.app.models.field import Claim, Transaction
from backend.app.financial.reconciliation import (
    match_salary_credits,
    reconcile_bank_statement_balances
)


def run_what_if_simulation(
    db: Session,
    case_id: str,
    hypothetical_adjustments: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Executes a counterfactual simulation on a case.
    Does NOT mutate any database rows or official audit chains.
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise ValueError(f"Case {case_id} not found.")

    sim_id = f"WHATIF-{uuid.uuid4().hex[:8]}"
    created_at = datetime.now(timezone.utc).isoformat()

    # Fetch latest run
    latest_run = (
        db.query(ProcessingRun)
        .filter(ProcessingRun.case_id == case_id)
        .order_by(ProcessingRun.created_at.desc())
        .first()
    )

    claims = []
    txs = []
    if latest_run:
        claims = db.query(Claim).filter(Claim.run_id == latest_run.id).all()
        txs = db.query(Transaction).filter(Transaction.run_id == latest_run.id).all()

    # Build simulation state with adjustments applied
    simulated_claims = []
    for c in claims:
        # Check if hypothetical net_amount applies
        new_amount = c.amount
        if "simulated_salary" in hypothetical_adjustments and c.claim_type == "SALARY_CLAIM":
            new_amount = Decimal(str(hypothetical_adjustments["simulated_salary"]))

        simulated_claims.append({
            "id": c.id,
            "claim_type": c.claim_type,
            "basis": getattr(c, "basis", "NET_SALARY"),
            "period_start": getattr(c, "period_start", "2026-05-01"),
            "period_end": getattr(c, "period_end", "2026-05-31"),
            "amount": new_amount,
            "original_amount": c.amount,
            "subject": getattr(c, "subject", "")
        })

    simulated_txs = []
    for t in txs:
        simulated_txs.append({
            "id": t.id,
            "page_id": getattr(t, "page_id", None),
            "bbox_normalized": getattr(t, "bbox_normalized", None),
            "transaction_date": getattr(t, "transaction_date", ""),
            "narration": getattr(t, "narration", ""),
            "transaction_type": getattr(t, "transaction_type", "CREDIT"),
            "amount": getattr(t, "amount", Decimal("0.00")),
            "running_balance": getattr(t, "running_balance", Decimal("0.00"))
        })

    # Run hypothetical reconciliation directly on adjusted dictionaries
    salary_recon = match_salary_credits(simulated_claims, simulated_txs)
    balance_recon = reconcile_bank_statement_balances(simulated_txs)

    return {
        "simulation_id": sim_id,
        "case_id": case.id,
        "reference_number": case.reference_number,
        "created_at": created_at,
        "is_isolated_hypothetical": True,
        "hypothetical_adjustments": hypothetical_adjustments,
        "simulated_outcomes": {
            "salary_reconciliation": salary_recon,
            "bank_balance_reconciliation": balance_recon
        },
        "summary": (
            "Hypothetical simulation completed. Under the proposed adjustments, "
            f"salary matching is {'CONSISTENT' if salary_recon.get('all_matched') else 'DISCREPANT'} "
            f"and ledger is {'BALANCED' if balance_recon.get('is_reconciled') else 'UNBALANCED'}."
        )
    }
