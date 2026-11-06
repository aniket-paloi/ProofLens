"""
ProofLens Reviewer Feedback & Disposition Analytics (Milestone 22 / Feature F17)
Aggregates reviewer disposition decisions and check-level metrics.
STRICT INVARIANT: Feedback analytics never triggers automatic online model retraining.
Preserves sovereign human curation and auditability.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.models.finding import Finding, ReviewAction
from backend.app.models.execution import CheckExecution


def get_reviewer_feedback_metrics(db: Session) -> Dict[str, Any]:
    """
    Computes aggregated disposition statistics across all findings and reviewer actions.
    """
    total_findings = db.query(Finding).count()

    # Dispositions
    unreviewed = db.query(Finding).filter(Finding.reviewer_disposition == "UNREVIEWED").count()
    confirmed = db.query(Finding).filter(Finding.reviewer_disposition == "CONFIRMED").count()
    dismissed = db.query(Finding).filter(Finding.reviewer_disposition == "DISMISSED").count()
    further_needed = db.query(Finding).filter(Finding.reviewer_disposition == "FURTHER_VERIFICATION_NEEDED").count()

    total_decided = confirmed + dismissed + further_needed

    # Reviewer Agreement Rate: confirmed vs dismissed
    agreement_rate = (confirmed / max(total_decided, 1)) if total_decided > 0 else 1.0
    dismissal_rate = (dismissed / max(total_decided, 1)) if total_decided > 0 else 0.0

    # Categorical breakdown
    categories = {}
    obs_types = db.query(Finding.observation_type, func.count(Finding.id)).group_by(Finding.observation_type).all()
    for o_type, count in obs_types:
        categories[o_type] = count

    # Review Actions count
    actions_count = db.query(ReviewAction).count()

    return {
        "metrics_generated_at": datetime.now(timezone.utc).isoformat(),
        "total_findings_recorded": total_findings,
        "review_progress": {
            "unreviewed_count": unreviewed,
            "decided_count": total_decided,
            "completion_rate": round(total_decided / max(total_findings, 1), 3)
        },
        "disposition_distribution": {
            "CONFIRMED": confirmed,
            "DISMISSED": dismissed,
            "FURTHER_VERIFICATION_NEEDED": further_needed,
            "UNREVIEWED": unreviewed
        },
        "rates": {
            "reviewer_confirmation_rate": round(agreement_rate, 3),
            "reviewer_dismissal_rate": round(dismissal_rate, 3)
        },
        "observation_type_breakdown": categories,
        "total_audit_review_actions": actions_count,
        "governance_guarantee": "Strictly descriptive metrics. Feedback data is archived for human-in-the-loop review only and NEVER triggers automated online retraining."
    }

