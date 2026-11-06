import os
from typing import Dict, Any, List, Optional
from decimal import Decimal
from backend.app.forensics.visual_baseline import (
    analyze_sharpness_variance,
    analyze_contrast_edge_discontinuity,
    save_crop_derivative
)
from backend.app.parsers.crosscheck import crosscheck_page_text_layers
from backend.app.financial.reconciliation import (
    reconcile_bank_statement_balances,
    match_salary_credits,
    check_employer_consistency
)

def tool_inspect_crop(image_path: str, bbox_normalized: List[float]) -> Dict[str, Any]:
    """Tool 1: Inspects a visual region crop, measuring sharpness and contrast edge boundary gradients."""
    sharp_res = analyze_sharpness_variance(image_path, bbox_normalized)
    edge_res = analyze_contrast_edge_discontinuity(image_path, bbox_normalized)
    crop_path = save_crop_derivative(image_path, bbox_normalized, crop_prefix="agent_inspect")

    return {
        "status": "COMPLETED",
        "crop_path": crop_path,
        "sharpness_ratio": sharp_res.get("sharpness_ratio", 1.0),
        "is_sharpness_anomaly": sharp_res.get("is_anomaly", False),
        "border_gradient_ratio": edge_res.get("border_ratio", 1.0),
        "is_edge_anomaly": edge_res.get("is_anomaly", False),
        "limitations": "Evaluated on 150 DPI raster derivative"
    }

def tool_crosscheck_text(pdf_path: str, page_number: int) -> Dict[str, Any]:
    """Tool 2: Crosschecks vector text layer vs visual rendering for invisible text, prompt injection, and baselines."""
    return crosscheck_page_text_layers(pdf_path, page_number)

def tool_reconcile_balance(transactions: List[Any]) -> Dict[str, Any]:
    """Tool 3: Validates bank statement arithmetic running balance ledger step-by-step."""
    return reconcile_bank_statement_balances(transactions)

def tool_match_salary_credit(salary_claims: List[Any], transactions: List[Any]) -> Dict[str, Any]:
    """Tool 4: Matches salary slip net pay claims against candidate bank deposits (single or split match)."""
    return match_salary_credits(salary_claims, transactions)

def tool_check_employer(fields: List[Any], transactions: List[Any]) -> Dict[str, Any]:
    """Tool 5: Evaluates employer entity name consistency across application, payslips, and bank narrations."""
    return check_employer_consistency(fields, transactions)

def tool_get_field_provenance(document_type: str, filename: str) -> Dict[str, Any]:
    """
    Tool 6: Classifies source provenance category:
    - KNOWN_DERIVATION: Single issuer known origin
    - POSSIBLE_SHARED_SOURCE: Common format or third-party payroll provider
    - INDEPENDENT_ACQUISITION: Independently acquired bank feed/statement
    - UNKNOWN_DEFAULT: Unverified acquisition channel
    """
    doc_lower = filename.lower()
    if "bank" in doc_lower or "statement" in doc_lower:
        category = "INDEPENDENT_ACQUISITION"
        basis = "Banking institution statement acquired through applicant submission"
        independent_confirmation = True
    elif "salary" in doc_lower or "payslip" in doc_lower:
        category = "POSSIBLE_SHARED_SOURCE"
        basis = "Corporate employer payroll department format"
        independent_confirmation = False
    elif "application" in doc_lower:
        category = "KNOWN_DERIVATION"
        basis = "Applicant loan onboarding form"
        independent_confirmation = False
    else:
        category = "UNKNOWN_DEFAULT"
        basis = "Unclassified document origin"
        independent_confirmation = False

    return {
        "provenance_category": category,
        "lineage_basis": basis,
        "provides_independent_confirmation": independent_confirmation,
        "note": "Agreeing values from shared sources do not constitute independent confirmation"
    }

def tool_suggest_disposition(
    findings: List[Dict[str, Any]],
    coverage_score: float
) -> Dict[str, Any]:
    """
    Tool 7: Synthesizes evidence across findings and coverage to recommend reviewer disposition.
    Adheres strictly to the Zero-Accusation Principle:
    - Recommends CONFIRMED, DISMISSED, or FURTHER_VERIFICATION_NEEDED.
    - Never declares 'fraud' or 'authentic'; states factual observation basis only.
    """
    critical_findings = [f for f in findings if f.get("severity") == "CRITICAL"]
    high_findings = [f for f in findings if f.get("severity") == "HIGH"]
    info_findings = [f for f in findings if f.get("severity") == "INFO"]

    if critical_findings:
        return {
            "recommended_disposition": "FURTHER_VERIFICATION_NEEDED",
            "justification": f"Observed {len(critical_findings)} critical finding(s) including adversarial text layer payloads. Automatic processing quarantined.",
            "requires_human_sovereign_review": True,
            "next_steps": [
                "Inspect raw PDF vector text streams",
                "Request physical certified document copies"
            ]
        }

    if high_findings:
        return {
            "recommended_disposition": "FURTHER_VERIFICATION_NEEDED",
            "justification": f"Observed {len(high_findings)} unresolved discrepancy finding(s) (e.g. arithmetic balance gaps or unaligned salary credits).",
            "requires_human_sovereign_review": True,
            "next_steps": [
                "Verify candidate alternative explanations with employer HR",
                "Request updated bank statements for missing dates"
            ]
        }

    if info_findings and all(f.get("severity") in ["INFO", "LOW"] for f in findings):
        has_splits = any("Split Payroll" in f.get("title", "") for f in findings)
        return {
            "recommended_disposition": "CONFIRMED" if coverage_score >= 0.85 else "FURTHER_VERIFICATION_NEEDED",
            "justification": "All financial extractions reconciled with legitimate alternative explanations (e.g. verified split payroll) and no visual splicing detected." if has_splits else "All submitted documents demonstrate internal arithmetic and text layer consistency.",
            "requires_human_sovereign_review": True,
            "next_steps": [
                "Proceed with standard credit risk assessment"
            ]
        }

    return {
        "recommended_disposition": "CONFIRMED" if coverage_score >= 0.85 else "FURTHER_VERIFICATION_NEEDED",
        "justification": f"Document packet verified with {coverage_score*100:.0f}% coverage without unaligned discrepancies.",
        "requires_human_sovereign_review": True,
        "next_steps": ["Proceed with credit assessment"]
    }

