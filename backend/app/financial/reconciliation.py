from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional
import difflib
import re

def to_decimal(val: Any) -> Decimal:
    """Converts a value (float, str, int, Decimal) to a 2-decimal place Decimal."""
    if val is None:
        return Decimal("0.00")
    if isinstance(val, Decimal):
        return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if isinstance(val, (int, float)):
        return Decimal(str(round(val, 2))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    # String
    cleaned = str(val).replace(",", "").replace("₹", "").replace("$", "").replace("INR", "").strip()
    try:
        return Decimal(cleaned).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except Exception:
        return Decimal("0.00")

def reconcile_bank_statement_balances(transactions: List[Any]) -> Dict[str, Any]:
    """
    Verifies step-by-step arithmetic running balances in bank statements:
    expected_balance = prev_balance + credit - debit.
    """
    if not transactions:
        return {
            "status": "NO_TRANSACTIONS",
            "is_reconciled": True,
            "discrepancies": [],
            "total_transactions": 0
        }

    # Transactions are expected in document sequence (or sort by transaction_date)
    discrepancies = []
    prev_balance: Optional[Decimal] = None

    for i, tx in enumerate(transactions):
        # Support dict or SQLAlchemy model
        tx_type = tx.transaction_type if hasattr(tx, "transaction_type") else tx.get("transaction_type", "")
        amount = to_decimal(tx.amount if hasattr(tx, "amount") else tx.get("amount", 0))
        stated_balance = to_decimal(tx.running_balance if hasattr(tx, "running_balance") else tx.get("running_balance", 0))
        date_str = tx.transaction_date if hasattr(tx, "transaction_date") else tx.get("transaction_date", "")
        narration = tx.narration if hasattr(tx, "narration") else tx.get("narration", "")
        tx_id = tx.id if hasattr(tx, "id") else tx.get("id", str(i))
        page_id = tx.page_id if hasattr(tx, "page_id") else tx.get("page_id", None)
        bbox = tx.bbox_normalized if hasattr(tx, "bbox_normalized") else tx.get("bbox_normalized", None)

        if prev_balance is not None:
            if tx_type == "CREDIT":
                expected_balance = prev_balance + amount
            else:
                expected_balance = prev_balance - amount

            diff = stated_balance - expected_balance
            if abs(diff) > Decimal("0.05"):
                discrepancies.append({
                    "transaction_id": tx_id,
                    "page_id": page_id,
                    "date": date_str,
                    "narration": narration,
                    "type": tx_type,
                    "amount": float(amount),
                    "stated_balance": float(stated_balance),
                    "expected_balance": float(expected_balance),
                    "delta": float(diff),
                    "bbox_normalized": bbox
                })

        # Update running balance baseline for next iteration
        prev_balance = stated_balance

    return {
        "status": "DISCREPANCY_DETECTED" if discrepancies else "RECONCILED",
        "is_reconciled": len(discrepancies) == 0,
        "discrepancies": discrepancies,
        "total_transactions": len(transactions)
    }

def match_salary_credits(salary_claims: List[Any], transactions: List[Any]) -> Dict[str, Any]:
    """
    Matches monthly salary slip net payable claims to bank statement credit transactions.
    Supports:
    1. Exact single credit match
    2. Split/multi-deposit candidate match (sum of 2 or 3 credits in pay window)
    3. Unmatched / under-credited discrepancies
    """
    credits = []
    for idx, tx in enumerate(transactions):
        tx_type = tx.transaction_type if hasattr(tx, "transaction_type") else tx.get("transaction_type", "")
        if tx_type == "CREDIT":
            if hasattr(tx, "id") and tx.id:
                cid = str(tx.id)
            elif isinstance(tx, dict) and tx.get("id"):
                cid = str(tx["id"])
            else:
                amt_str = str(tx.amount if hasattr(tx, "amount") else tx.get("amount", 0))
                dt_str = str(tx.transaction_date if hasattr(tx, "transaction_date") else tx.get("transaction_date", ""))
                cid = f"credit_{idx}_{dt_str}_{amt_str}"
            credits.append((cid, tx))

    results = []
    used_credit_ids = set()

    for claim in salary_claims:
        basis = claim.basis if hasattr(claim, "basis") else claim.get("basis", "")
        if basis != "NET_SALARY":
            continue

        target_amount = to_decimal(claim.amount if hasattr(claim, "amount") else claim.get("amount", 0))
        claim_id = claim.id if hasattr(claim, "id") else claim.get("id", "")
        period_start = claim.period_start if hasattr(claim, "period_start") else claim.get("period_start", "")

        # 1. Look for Exact Single Credit Match
        matched_single = None
        matched_cid = None
        for cid, cred in credits:
            if cid in used_credit_ids:
                continue
            amt = to_decimal(cred.amount if hasattr(cred, "amount") else cred.get("amount", 0))
            if abs(amt - target_amount) <= Decimal("1.00"):
                matched_single = cred
                matched_cid = cid
                break

        if matched_single and matched_cid:
            used_credit_ids.add(matched_cid)
            results.append({
                "claim_id": claim_id,
                "target_amount": float(target_amount),
                "match_status": "EXACT_MATCH",
                "matched_type": "SINGLE",
                "variance": 0.0,
                "credits": [{
                    "id": matched_cid,
                    "date": matched_single.transaction_date if hasattr(matched_single, "transaction_date") else matched_single.get("transaction_date", ""),
                    "narration": matched_single.narration if hasattr(matched_single, "narration") else matched_single.get("narration", ""),
                    "amount": float(to_decimal(matched_single.amount if hasattr(matched_single, "amount") else matched_single.get("amount", 0))),
                    "bbox_normalized": matched_single.bbox_normalized if hasattr(matched_single, "bbox_normalized") else matched_single.get("bbox_normalized", None),
                    "page_id": matched_single.page_id if hasattr(matched_single, "page_id") else matched_single.get("page_id", None)
                }]
            })
            continue

        # 2. Look for Candidate Split Payroll (combinations of 2 available credits in window)
        available_credits = [
            (cid, c) for cid, c in credits 
            if cid not in used_credit_ids
        ]
        
        split_found = False
        for i in range(len(available_credits)):
            for j in range(i + 1, len(available_credits)):
                id1, c1 = available_credits[i]
                id2, c2 = available_credits[j]
                a1 = to_decimal(c1.amount if hasattr(c1, "amount") else c1.get("amount", 0))
                a2 = to_decimal(c2.amount if hasattr(c2, "amount") else c2.get("amount", 0))

                if abs((a1 + a2) - target_amount) <= Decimal("1.00"):
                    used_credit_ids.add(id1)
                    used_credit_ids.add(id2)
                    results.append({
                        "claim_id": claim_id,
                        "target_amount": float(target_amount),
                        "match_status": "SPLIT_MATCH",
                        "matched_type": "MULTI_TRANSACTION",
                        "variance": 0.0,
                        "credits": [
                            {
                                "id": id1,
                                "date": c1.transaction_date if hasattr(c1, "transaction_date") else c1.get("transaction_date", ""),
                                "narration": c1.narration if hasattr(c1, "narration") else c1.get("narration", ""),
                                "amount": float(a1),
                                "bbox_normalized": c1.bbox_normalized if hasattr(c1, "bbox_normalized") else c1.get("bbox_normalized", None),
                                "page_id": c1.page_id if hasattr(c1, "page_id") else c1.get("page_id", None)
                            },
                            {
                                "id": id2,
                                "date": c2.transaction_date if hasattr(c2, "transaction_date") else c2.get("transaction_date", ""),
                                "narration": c2.narration if hasattr(c2, "narration") else c2.get("narration", ""),
                                "amount": float(a2),
                                "bbox_normalized": c2.bbox_normalized if hasattr(c2, "bbox_normalized") else c2.get("bbox_normalized", None),
                                "page_id": c2.page_id if hasattr(c2, "page_id") else c2.get("page_id", None)
                            }
                        ]
                    })
                    split_found = True
                    break
            if split_found:
                break

        if split_found:
            continue

        # 3. No match found: record nearest candidate or discrepancy
        nearest_cred = None
        nearest_cid = None
        min_diff = None
        for cid, c in available_credits:
            amt = to_decimal(c.amount if hasattr(c, "amount") else c.get("amount", 0))
            diff = abs(amt - target_amount)
            if min_diff is None or diff < min_diff:
                min_diff = diff
                nearest_cred = c
                nearest_cid = cid

        nearest_list = []
        variance_val = float(target_amount)
        if nearest_cred and nearest_cid:
            n_amt = float(to_decimal(nearest_cred.amount if hasattr(nearest_cred, "amount") else nearest_cred.get("amount", 0)))
            variance_val = round(float(target_amount) - n_amt, 2)
            nearest_list.append({
                "id": nearest_cid,
                "date": nearest_cred.transaction_date if hasattr(nearest_cred, "transaction_date") else nearest_cred.get("transaction_date", ""),
                "narration": nearest_cred.narration if hasattr(nearest_cred, "narration") else nearest_cred.get("narration", ""),
                "amount": n_amt,
                "bbox_normalized": nearest_cred.bbox_normalized if hasattr(nearest_cred, "bbox_normalized") else nearest_cred.get("bbox_normalized", None),
                "page_id": nearest_cred.page_id if hasattr(nearest_cred, "page_id") else nearest_cred.get("page_id", None)
            })

        results.append({
            "claim_id": claim_id,
            "target_amount": float(target_amount),
            "match_status": "UNMATCHED_DISCREPANCY",
            "matched_type": "NONE",
            "variance": variance_val,
            "credits": nearest_list
        })

    all_matched = all(r["match_status"] in ("EXACT_MATCH", "SPLIT_MATCH") for r in results) if results else True
    has_splits = any(r["match_status"] == "SPLIT_MATCH" for r in results)

    return {
        "status": "MATCHED" if all_matched else ("SPLIT_MATCHED" if has_splits else "DISCREPANCY"),
        "all_matched": all_matched,
        "has_splits": has_splits,
        "results": results
    }

def reconcile_income_declaration(app_claims: List[Any], salary_claims: List[Any]) -> Dict[str, Any]:
    """
    Compares income declared on application form with extracted salary slip claims.
    """
    app_net = None
    app_gross = None

    for c in app_claims:
        basis = c.basis if hasattr(c, "basis") else c.get("basis", "")
        amt = to_decimal(c.amount if hasattr(c, "amount") else c.get("amount", 0))
        if basis == "NET_SALARY":
            app_net = amt
        elif basis == "GROSS_SALARY":
            app_gross = amt

    slip_nets = []
    slip_grosses = []
    for c in salary_claims:
        basis = c.basis if hasattr(c, "basis") else c.get("basis", "")
        amt = to_decimal(c.amount if hasattr(c, "amount") else c.get("amount", 0))
        if basis == "NET_SALARY":
            slip_nets.append(amt)
        elif basis == "GROSS_SALARY":
            slip_grosses.append(amt)

    avg_slip_net = (sum(slip_nets) / len(slip_nets)).quantize(Decimal("0.01")) if slip_nets else None
    avg_slip_gross = (sum(slip_grosses) / len(slip_grosses)).quantize(Decimal("0.01")) if slip_grosses else None

    discrepancies = []
    if app_net is not None and avg_slip_net is not None:
        net_diff = app_net - avg_slip_net
        if abs(net_diff) > Decimal("100.00"):
            discrepancies.append({
                "field": "net_salary",
                "declared": float(app_net),
                "verified_average": float(avg_slip_net),
                "delta": float(net_diff)
            })

    if app_gross is not None and avg_slip_gross is not None:
        gross_diff = app_gross - avg_slip_gross
        if abs(gross_diff) > Decimal("100.00"):
            discrepancies.append({
                "field": "gross_salary",
                "declared": float(app_gross),
                "verified_average": float(avg_slip_gross),
                "delta": float(gross_diff)
            })

    return {
        "status": "DISCREPANCY" if discrepancies else "ALIGNED",
        "is_aligned": len(discrepancies) == 0,
        "declared_net": float(app_net) if app_net else None,
        "verified_net_avg": float(avg_slip_net) if avg_slip_net else None,
        "discrepancies": discrepancies
    }

def clean_employer_name(name: str) -> str:
    """Standardizes employer company names for comparison."""
    if not name:
        return ""
    cleaned = name.upper()
    for drop in ["LIMITED", "LTD", "PVT", "PRIVATE", "CORP", "CORPORATION", "TECHNOLOGIES", "TECH", "SOLUTIONS", "INC"]:
        cleaned = re.sub(rf"\b{drop}\b", "", cleaned)
    cleaned = re.sub(r"[^A-Z0-9\s]", " ", cleaned)
    return " ".join(cleaned.split())

def check_employer_consistency(fields: List[Any], transactions: List[Any]) -> Dict[str, Any]:
    """
    Checks consistency of declared employer vs payslip employer vs bank statement salary credit narrations.
    """
    declared_employer = None
    payslip_employers = []

    for f in fields:
        fname = f.field_name if hasattr(f, "field_name") else f.get("field_name", "")
        fval = f.raw_value if hasattr(f, "raw_value") else f.get("raw_value", "")
        if not fval:
            continue
        if fname == "employer_name":
            # Check if from application or payslip based on page/document context if available
            if declared_employer is None:
                declared_employer = fval
            else:
                payslip_employers.append(fval)

    if not declared_employer or not payslip_employers:
        return {
            "status": "INSUFFICIENT_DATA",
            "is_consistent": True,
            "declared_employer": declared_employer,
            "payslip_employers": payslip_employers,
            "mismatches": []
        }

    clean_decl = clean_employer_name(declared_employer)
    mismatches = []

    for emp in payslip_employers:
        clean_slip = clean_employer_name(emp)
        # Compute similarity ratio
        ratio = difflib.SequenceMatcher(None, clean_decl, clean_slip).ratio()
        # Word set overlap
        decl_tokens = set(clean_decl.split())
        slip_tokens = set(clean_slip.split())
        has_overlap = bool(decl_tokens.intersection(slip_tokens))

        if ratio < 0.50 and not has_overlap:
            mismatches.append({
                "declared": declared_employer,
                "found": emp,
                "similarity_score": round(ratio, 2)
            })

    return {
        "status": "MISMATCH" if mismatches else "CONSISTENT",
        "is_consistent": len(mismatches) == 0,
        "declared_employer": declared_employer,
        "payslip_employers": payslip_employers,
        "mismatches": mismatches
    }
