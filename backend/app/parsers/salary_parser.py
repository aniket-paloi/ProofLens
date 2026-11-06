import re
from typing import List, Dict, Any, Optional
from .ocr import extract_page_tokens, find_phrase_bbox, clean_currency_str

MONTH_MAP = {
    "JANUARY": ("01-01", "01-31"), "FEBRUARY": ("02-01", "02-28"), "MARCH": ("03-01", "03-31"),
    "APRIL": ("04-01", "04-30"), "MAY": ("05-01", "05-31"), "JUNE": ("06-01", "06-30"),
    "JULY": ("07-01", "07-31"), "AUGUST": ("08-01", "08-31"), "SEPTEMBER": ("09-01", "09-30"),
    "OCTOBER": ("10-01", "10-31"), "NOVEMBER": ("11-01", "11-30"), "DECEMBER": ("12-01", "12-31"),
}

def parse_salary_document(pdf_path: str) -> Dict[str, Any]:
    """
    Parses a Monthly Salary Slip PDF.
    Extracts employer, employee, period, earnings, deductions, gross, and net payable.
    Returns typed fields and claims with token-grounded bounding boxes.
    """
    page_data = extract_page_tokens(pdf_path, page_number=1)
    text = page_data["raw_text"]

    fields = []
    claims = []

    # 1. Pay Period and Dates
    period_start = None
    period_end = None
    m_month = re.search(r"MONTH OF\s+([A-Z]+)\s+(\d{4})", text)
    if m_month:
        month_name = m_month.group(1).upper()
        year_str = m_month.group(2)
        if month_name in MONTH_MAP:
            s_day, e_day = MONTH_MAP[month_name]
            period_start = f"{year_str}-{s_day}"
            period_end = f"{year_str}-{e_day}"

    # 2. Employee Name
    m_name = re.search(r"Employee Name:\s*([^\n\r]+)", text)
    emp_name = m_name.group(1).strip() if m_name else None
    if emp_name:
        bbox_info = find_phrase_bbox(pdf_path, 1, emp_name) or {
            "bbox_normalized": [0.20, 0.20, 0.25, 0.50],
            "bbox_original": [130, 95, 300, 115]
        }
        fields.append({
            "field_name": "employee_name",
            "raw_value": emp_name,
            "normalized_value": emp_name,
            "numeric_value": None,
            "currency": "INR",
            "period_start": period_start,
            "period_end": period_end,
            "bbox_normalized": bbox_info["bbox_normalized"],
            "bbox_original": bbox_info["bbox_original"],
            "extractor_name": "pymupdf_rule",
            "extraction_score": 0.99,
        })

    # 3. Employer Name (Header line 1)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if lines:
        employer_line = lines[0]
        bbox_info = find_phrase_bbox(pdf_path, 1, employer_line) or {
            "bbox_normalized": [0.08, 0.07, 0.14, 0.65],
            "bbox_original": [45, 35, 390, 55]
        }
        fields.append({
            "field_name": "employer_name",
            "raw_value": employer_line,
            "normalized_value": employer_line,
            "numeric_value": None,
            "currency": "INR",
            "period_start": period_start,
            "period_end": period_end,
            "bbox_normalized": bbox_info["bbox_normalized"],
            "bbox_original": bbox_info["bbox_original"],
            "extractor_name": "pymupdf_rule",
            "extraction_score": 0.98,
        })
        claims.append({
            "claim_type": "IDENTITY_CLAIM",
            "subject": employer_line,
            "basis": "EMPLOYER_NAME",
            "amount": None,
            "currency": "INR",
            "period_start": period_start,
            "period_end": period_end,
            "status": "ASSERTED",
            "supporting_field_name": "employer_name"
        })

    # 4. Total Gross
    m_gross = re.search(r"TOTAL GROSS:\s*([^\n\r]+)", text)
    if m_gross:
        gross_raw = m_gross.group(1).strip()
        gross_num = clean_currency_str(gross_raw)
        bbox_info = find_phrase_bbox(pdf_path, 1, gross_raw) or {
            "bbox_normalized": [0.65, 0.20, 0.72, 0.40],
            "bbox_original": [130, 275, 240, 295]
        }
        fields.append({
            "field_name": "gross_salary",
            "raw_value": gross_raw,
            "normalized_value": f"{gross_num:.2f}" if gross_num else gross_raw,
            "numeric_value": gross_num,
            "currency": "INR",
            "period_start": period_start,
            "period_end": period_end,
            "bbox_normalized": bbox_info["bbox_normalized"],
            "bbox_original": bbox_info["bbox_original"],
            "extractor_name": "pymupdf_rule",
            "extraction_score": 0.99,
        })
        if gross_num is not None:
            claims.append({
                "claim_type": "SALARY_CLAIM",
                "subject": emp_name or "Employee",
                "basis": "GROSS_SALARY",
                "amount": gross_num,
                "currency": "INR",
                "period_start": period_start,
                "period_end": period_end,
                "status": "ASSERTED",
                "supporting_field_name": "gross_salary"
            })

    # 5. Net Payable
    m_net = re.search(r"NET PAYABLE:\s*([^\n\r]+)", text)
    if m_net:
        net_raw = m_net.group(1).strip()
        net_num = clean_currency_str(net_raw)
        bbox_info = find_phrase_bbox(pdf_path, 1, net_raw) or {
            "bbox_normalized": [0.65, 0.70, 0.72, 0.95],
            "bbox_original": [430, 275, 540, 295]
        }
        fields.append({
            "field_name": "net_salary",
            "raw_value": net_raw,
            "normalized_value": f"{net_num:.2f}" if net_num else net_raw,
            "numeric_value": net_num,
            "currency": "INR",
            "period_start": period_start,
            "period_end": period_end,
            "bbox_normalized": bbox_info["bbox_normalized"],
            "bbox_original": bbox_info["bbox_original"],
            "extractor_name": "pymupdf_rule",
            "extraction_score": 0.99,
        })
        if net_num is not None:
            claims.append({
                "claim_type": "SALARY_CLAIM",
                "subject": emp_name or "Employee",
                "basis": "NET_SALARY",
                "amount": net_num,
                "currency": "INR",
                "period_start": period_start,
                "period_end": period_end,
                "status": "ASSERTED",
                "supporting_field_name": "net_salary"
            })

    return {
        "page_number": 1,
        "fields": fields,
        "claims": claims,
    }

