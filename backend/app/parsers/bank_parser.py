import re
from typing import List, Dict, Any, Optional
from .ocr import extract_page_tokens, find_phrase_bbox, clean_currency_str

SALARY_KEYWORDS = [
    "SALARY", "SAL", "ACH/SALARY", "NEFT/SALARY", "PAYROLL", "INCENTIVE", "CORP CREDIT"
]

def parse_bank_statement_document(pdf_path: str) -> Dict[str, Any]:
    """
    Parses a Bank Statement PDF using token geometry row clustering.
    Extracts account metadata, transaction table rows (debits, credits, balances),
    and flags salary candidate credits.
    """
    page_data = extract_page_tokens(pdf_path, page_number=1)
    text = page_data["raw_text"]
    tokens = page_data["tokens"]
    height = page_data["height_pts"]
    width = page_data["width_pts"]

    fields = []
    transactions = []
    claims = []

    # 1. Account Name
    m_name = re.search(r"Account Name:\s*([^\n\r]+)", text)
    if m_name:
        acc_name = m_name.group(1).strip()
        bbox_info = find_phrase_bbox(pdf_path, 1, acc_name) or {
            "bbox_normalized": [0.15, 0.22, 0.18, 0.50],
            "bbox_original": [140, 130, 300, 150]
        }
        fields.append({
            "field_name": "account_name",
            "raw_value": acc_name,
            "normalized_value": acc_name,
            "numeric_value": None,
            "currency": "INR",
            "bbox_normalized": bbox_info["bbox_normalized"],
            "bbox_original": bbox_info["bbox_original"],
            "extractor_name": "pymupdf_rule",
            "extraction_score": 0.99,
        })
        claims.append({
            "claim_type": "IDENTITY_CLAIM",
            "subject": acc_name,
            "basis": "ACCOUNT_HOLDER",
            "amount": None,
            "currency": "INR",
            "status": "ASSERTED",
            "supporting_field_name": "account_name"
        })

    # 2. Account Number
    m_acc = re.search(r"Account Number:\s*([^\n\r]+)", text)
    if m_acc:
        acc_num = m_acc.group(1).strip()
        bbox_info = find_phrase_bbox(pdf_path, 1, acc_num) or {
            "bbox_normalized": [0.15, 0.72, 0.18, 0.95],
            "bbox_original": [440, 130, 540, 150]
        }
        fields.append({
            "field_name": "account_number",
            "raw_value": acc_num,
            "normalized_value": acc_num,
            "numeric_value": None,
            "currency": "INR",
            "bbox_normalized": bbox_info["bbox_normalized"],
            "bbox_original": bbox_info["bbox_original"],
            "extractor_name": "pymupdf_rule",
            "extraction_score": 0.99,
        })

    # 3. Statement Period
    m_per = re.search(r"Statement Period:\s*([^\n\r]+)", text)
    if m_per:
        period_str = m_per.group(1).strip()
        bbox_info = find_phrase_bbox(pdf_path, 1, period_str) or {
            "bbox_normalized": [0.18, 0.22, 0.21, 0.55],
            "bbox_original": [140, 150, 330, 170]
        }
        fields.append({
            "field_name": "statement_period",
            "raw_value": period_str,
            "normalized_value": period_str,
            "numeric_value": None,
            "currency": "INR",
            "bbox_normalized": bbox_info["bbox_normalized"],
            "bbox_original": bbox_info["bbox_original"],
            "extractor_name": "pymupdf_rule",
            "extraction_score": 0.99,
        })

    # 4. Cluster Tokens into Horizontal Table Rows (Token Y-Binning)
    # Filter tokens that fall in the table area (y0 >= 190)
    table_tokens = [t for t in tokens if t["bbox_original"][1] >= 190]
    
    # Group tokens by vertical line (tolerance: +/- 6 pts)
    rows: List[List[Dict[str, Any]]] = []
    for t in sorted(table_tokens, key=lambda x: (x["bbox_original"][1], x["bbox_original"][0])):
        placed = False
        for r in rows:
            # Check if within vertical tolerance of this row
            if abs(r[0]["bbox_original"][1] - t["bbox_original"][1]) <= 6.0:
                r.append(t)
                placed = True
                break
        if not placed:
            rows.append([t])

    date_regex = re.compile(r"^\d{2}-[A-Z]{3}-\d{4}$")

    for r in rows:
        # Sort tokens in row horizontally
        r_sorted = sorted(r, key=lambda x: x["bbox_original"][0])
        row_text = " ".join([t["text"] for t in r_sorted])

        # Check if first word is a date (e.g. 01-MAY-2026)
        first_word = r_sorted[0]["text"]
        if not date_regex.match(first_word):
            continue

        tx_date = first_word
        rem_tokens = r_sorted[1:]
        if not rem_tokens:
            continue

        # Ignore opening balance row
        if any("OPENING" in t["text"].upper() for t in rem_tokens):
            continue

        # Extract amounts from tokens (numbers matching \d+[\d,]*\.\d{2})
        num_tokens = []
        narration_tokens = []
        for t in rem_tokens:
            val = t["text"].replace(",", "")
            try:
                float(val)
                num_tokens.append(t)
            except ValueError:
                narration_tokens.append(t)

        narration = " ".join([t["text"] for t in narration_tokens]).strip()

        # Check salary keywords
        narration_upper = narration.upper()
        is_salary_candidate = 1 if any(kw in narration_upper for kw in SALARY_KEYWORDS) else 0

        # Numbers: if 2 numbers found, [tx_amount, balance]
        amount = 0.0
        running_bal = None
        if len(num_tokens) >= 2:
            amount = clean_currency_str(num_tokens[0]["text"]) or 0.0
            running_bal = clean_currency_str(num_tokens[1]["text"])
        elif len(num_tokens) == 1:
            amount = clean_currency_str(num_tokens[0]["text"]) or 0.0

        tx_type = "CREDIT" if (is_salary_candidate or "CR" in row_text.upper() or "REFUND" in narration_upper) else "DEBIT"

        # Calculate enclosing bounding box for this transaction row
        y0 = min(t["bbox_original"][1] for t in r_sorted)
        y1 = max(t["bbox_original"][3] for t in r_sorted)
        x0 = min(t["bbox_original"][0] for t in r_sorted)
        x1 = max(t["bbox_original"][2] for t in r_sorted)

        ymin = round(max(0.0, min(1.0, y0 / height)), 4)
        xmin = round(max(0.0, min(1.0, x0 / width)), 4)
        ymax = round(max(0.0, min(1.0, y1 / height)), 4)
        xmax = round(max(0.0, min(1.0, x1 / width)), 4)

        tx_dict = {
            "transaction_date": tx_date,
            "narration": narration,
            "transaction_type": tx_type,
            "amount": amount,
            "running_balance": running_bal,
            "is_salary_candidate": is_salary_candidate,
            "bbox_normalized": [ymin, xmin, ymax, xmax],
        }
        transactions.append(tx_dict)

        # Generate claim for salary candidate credits
        if is_salary_candidate and tx_type == "CREDIT":
            claims.append({
                "claim_type": "SALARY_CLAIM",
                "subject": fields[0]["raw_value"] if fields else "Account Holder",
                "basis": "BANK_CREDIT",
                "amount": amount,
                "currency": "INR",
                "period_start": tx_date,
                "period_end": tx_date,
                "status": "ASSERTED",
                "supporting_field_name": narration
            })

    return {
        "page_number": 1,
        "fields": fields,
        "transactions": transactions,
        "claims": claims,
    }
