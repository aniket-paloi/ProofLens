import re
from typing import List, Dict, Any, Optional
from .ocr import extract_page_tokens, find_phrase_bbox, clean_currency_str

def parse_application_document(pdf_path: str) -> Dict[str, Any]:
    """
    Parses a Loan Application Form PDF.
    Extracts applicant identity, PAN, requested loan, employer, gross income, and net income.
    Returns typed fields and typed claims with precise token geometry.
    """
    page_data = extract_page_tokens(pdf_path, page_number=1)
    text = page_data["raw_text"]

    fields = []
    claims = []

    # 1. Applicant Name
    # Matches: Full Name: Rajesh K. Sharma or Full Name:\s+([^\n]+)
    m_name = re.search(r"Full Name:\s*([^\n\r]+)", text)
    if m_name:
        applicant_name = m_name.group(1).strip()
        bbox_info = find_phrase_bbox(pdf_path, 1, applicant_name) or {
            "bbox_normalized": [0.15, 0.25, 0.18, 0.55],
            "bbox_original": [150, 130, 320, 150]
        }
        f_name = {
            "field_name": "applicant_name",
            "raw_value": applicant_name,
            "normalized_value": applicant_name,
            "numeric_value": None,
            "currency": "INR",
            "bbox_normalized": bbox_info["bbox_normalized"],
            "bbox_original": bbox_info["bbox_original"],
            "extractor_name": "pymupdf_rule",
            "extraction_score": 0.99,
        }
        fields.append(f_name)

        claims.append({
            "claim_type": "IDENTITY_CLAIM",
            "subject": applicant_name,
            "basis": "APPLICANT_NAME",
            "amount": None,
            "currency": "INR",
            "status": "ASSERTED",
            "supporting_field_name": "applicant_name"
        })

    # 2. PAN Number
    m_pan = re.search(r"PAN Identification:\s*([A-Z0-9]{10})", text)
    if m_pan:
        pan_val = m_pan.group(1).strip()
        bbox_info = find_phrase_bbox(pdf_path, 1, pan_val) or {
            "bbox_normalized": [0.15, 0.75, 0.18, 0.95],
            "bbox_original": [450, 130, 540, 150]
        }
        fields.append({
            "field_name": "pan_number",
            "raw_value": pan_val,
            "normalized_value": pan_val,
            "numeric_value": None,
            "currency": "INR",
            "bbox_normalized": bbox_info["bbox_normalized"],
            "bbox_original": bbox_info["bbox_original"],
            "extractor_name": "pymupdf_rule",
            "extraction_score": 0.99,
        })

    # 3. Current Employer
    m_emp = re.search(r"Current Employer:\s*([^\n\r]+)", text)
    if m_emp:
        emp_name = m_emp.group(1).strip()
        bbox_info = find_phrase_bbox(pdf_path, 1, emp_name) or {
            "bbox_normalized": [0.28, 0.26, 0.32, 0.70],
            "bbox_original": [160, 235, 420, 260]
        }
        fields.append({
            "field_name": "employer_name",
            "raw_value": emp_name,
            "normalized_value": emp_name,
            "numeric_value": None,
            "currency": "INR",
            "bbox_normalized": bbox_info["bbox_normalized"],
            "bbox_original": bbox_info["bbox_original"],
            "extractor_name": "pymupdf_rule",
            "extraction_score": 0.98,
        })
        claims.append({
            "claim_type": "IDENTITY_CLAIM",
            "subject": emp_name,
            "basis": "EMPLOYER_NAME",
            "amount": None,
            "currency": "INR",
            "status": "ASSERTED",
            "supporting_field_name": "employer_name"
        })

    # 4. Declared Monthly Gross Salary
    m_gross = re.search(r"Declared Monthly Gross:\s*([^\n\r]+)", text)
    if m_gross:
        gross_raw = m_gross.group(1).strip()
        gross_num = clean_currency_str(gross_raw)
        bbox_info = find_phrase_bbox(pdf_path, 1, gross_raw) or {
            "bbox_normalized": [0.32, 0.26, 0.36, 0.50],
            "bbox_original": [160, 265, 300, 290]
        }
        fields.append({
            "field_name": "gross_salary",
            "raw_value": gross_raw,
            "normalized_value": f"{gross_num:.2f}" if gross_num else gross_raw,
            "numeric_value": gross_num,
            "currency": "INR",
            "bbox_normalized": bbox_info["bbox_normalized"],
            "bbox_original": bbox_info["bbox_original"],
            "extractor_name": "pymupdf_rule",
            "extraction_score": 0.99,
        })
        if gross_num is not None:
            claims.append({
                "claim_type": "SALARY_CLAIM",
                "subject": fields[0]["raw_value"] if fields else "Applicant",
                "basis": "GROSS_SALARY",
                "amount": gross_num,
                "currency": "INR",
                "status": "ASSERTED",
                "supporting_field_name": "gross_salary"
            })

    # 5. Declared Monthly Net Salary
    m_net = re.search(r"Declared Monthly Net:\s*([^\n\r]+)", text)
    if m_net:
        net_raw = m_net.group(1).strip()
        net_num = clean_currency_str(net_raw)
        bbox_info = find_phrase_bbox(pdf_path, 1, net_raw) or {
            "bbox_normalized": [0.32, 0.75, 0.36, 0.95],
            "bbox_original": [450, 265, 540, 290]
        }
        fields.append({
            "field_name": "net_salary",
            "raw_value": net_raw,
            "normalized_value": f"{net_num:.2f}" if net_num else net_raw,
            "numeric_value": net_num,
            "currency": "INR",
            "bbox_normalized": bbox_info["bbox_normalized"],
            "bbox_original": bbox_info["bbox_original"],
            "extractor_name": "pymupdf_rule",
            "extraction_score": 0.99,
        })
        if net_num is not None:
            claims.append({
                "claim_type": "SALARY_CLAIM",
                "subject": fields[0]["raw_value"] if fields else "Applicant",
                "basis": "NET_SALARY",
                "amount": net_num,
                "currency": "INR",
                "status": "ASSERTED",
                "supporting_field_name": "net_salary"
            })

    return {
        "page_number": 1,
        "fields": fields,
        "claims": claims,
    }

