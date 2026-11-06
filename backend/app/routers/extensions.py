"""
ProofLens Extended Capabilities API Router (Milestones 17-22)
Wires Evaluation, Robustness, FraudSim Lab, What-If Branching, and Reviewer Analytics.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from backend.app.core.database import get_db
from backend.evaluation.eval_suite import run_blind_evaluation
from backend.app.lab.fraudsim import list_lab_scenarios, generate_synthetic_specimen
from backend.app.simulation.what_if import run_what_if_simulation
from backend.app.analytics.feedback import get_reviewer_feedback_metrics

router = APIRouter(prefix="/extensions", tags=["Extensions & Advanced Capabilities"])


@router.get("/evaluation/benchmark")
def get_evaluation_benchmark(db: Session = Depends(get_db)):
    """Runs or retrieves the blind benchmark on held-out test packets."""
    try:
        return run_blind_evaluation(db=db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lab/scenarios")
def get_lab_scenarios():
    """Lists available FraudSim laboratory scenarios."""
    return list_lab_scenarios()


@router.post("/lab/generate")
def create_lab_specimen(payload: Dict[str, Any]):
    """Generates an isolated synthetic test specimen."""
    scenario_id = payload.get("scenario_id", "SCN_SALARY_INFLATION")
    params = payload.get("parameters", {})
    return generate_synthetic_specimen(scenario_id, params)


@router.post("/cases/{case_id}/what-if")
def create_what_if_simulation(case_id: str, payload: Dict[str, Any], db: Session = Depends(get_db)):
    """Runs an isolated what-if hypothetical simulation without mutating case records."""
    try:
        return run_what_if_simulation(db=db, case_id=case_id, hypothetical_adjustments=payload)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))


@router.get("/analytics/reviewer-feedback")
def get_analytics_metrics(db: Session = Depends(get_db)):
    """Returns aggregated reviewer disposition metrics with zero-online-retraining guarantee."""
    return get_reviewer_feedback_metrics(db)

