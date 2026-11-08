import os
import json
from typing import List, Dict, Any
from .models import PacketCaseDef, ScenarioType, SplitType
from .pdf_builder import build_application_form, build_salary_slip, build_bank_statement

def get_12_curated_packet_definitions() -> List[PacketCaseDef]:
    """Returns the 12 curated fictional loan packet definitions across Train, Val, and Test splits."""
    return [
        # --- TRAIN SPLIT (6 Cases) ---
        PacketCaseDef(
            reference_number="LOAN-2026-TR01",
            applicant_name="Rajesh K. Sharma",
            employer_declared="Tata Consultancy Services Ltd",
            employer_actual="Tata Consultancy Services Ltd",
            pan_number="ABCPS1234A",
            loan_amount=2500000,
            gross_salary_declared=120000,
            net_salary_declared=95000,
            gross_salary_slip=120000,
            net_salary_slip=95000,
            bank_credits_monthly=[
                [{"amount": 95000, "narration": "ACH/SALARY/TCS LTD/APR", "date": "01-MAY-2026"}],
                [{"amount": 95000, "narration": "ACH/SALARY/TCS LTD/MAY", "date": "01-JUN-2026"}],
                [{"amount": 95000, "narration": "ACH/SALARY/TCS LTD/JUN", "date": "01-JUL-2026"}]
            ],
            scenario=ScenarioType.CLEAN_CONSISTENT,
            split=SplitType.TRAIN,
            description="Verified baseline: TCS corporate payroll matching application declaration exactly.",
            expected_findings=[]
        ),
        PacketCaseDef(
            reference_number="LOAN-2026-TR02",
            applicant_name="Priya N. Iyer",
            employer_declared="Infosys Technologies Ltd",
            employer_actual="Infosys Technologies Ltd",
            pan_number="BKPPI9876B",
            loan_amount=1800000,
            gross_salary_declared=85000,
            net_salary_declared=68000,
            gross_salary_slip=85000,
            net_salary_slip=68000,
            bank_credits_monthly=[
                [{"amount": 68000, "narration": "NEFT/INFOSYS TECH/SAL", "date": "30-APR-2026"}],
                [{"amount": 68000, "narration": "NEFT/INFOSYS TECH/SAL", "date": "31-MAY-2026"}],
                [{"amount": 68000, "narration": "NEFT/INFOSYS TECH/SAL", "date": "30-JUN-2026"}]
            ],
            scenario=ScenarioType.CLEAN_CONSISTENT,
            split=SplitType.TRAIN,
            description="Clean consistent case with month-end credit schedule.",
            expected_findings=[]
        ),
        PacketCaseDef(
            reference_number="LOAN-2026-TR03",
            applicant_name="Ankit Verma",
            employer_declared="Reliance Jio Infocomm Ltd",
            employer_actual="Reliance Jio Infocomm Ltd",
            pan_number="CHIPV5544C",
            loan_amount=2200000,
            gross_salary_declared=110000,
            net_salary_declared=88000,
            gross_salary_slip=110000,
            net_salary_slip=88000,
            bank_credits_monthly=[
                [
                    {"amount": 55000, "narration": "ACH/SALARY/RELIANCE JIO", "date": "01-MAY-2026"},
                    {"amount": 33000, "narration": "NEFT/INCENTIVE/RELIANCE", "date": "03-MAY-2026"}
                ],
                [
                    {"amount": 55000, "narration": "ACH/SALARY/RELIANCE JIO", "date": "01-JUN-2026"},
                    {"amount": 33000, "narration": "NEFT/INCENTIVE/RELIANCE", "date": "03-JUN-2026"}
                ],
                [
                    {"amount": 55000, "narration": "ACH/SALARY/RELIANCE JIO", "date": "01-JUL-2026"},
                    {"amount": 33000, "narration": "NEFT/INCENTIVE/RELIANCE", "date": "03-JUL-2026"}
                ]
            ],
            scenario=ScenarioType.LEGITIMATE_SPLIT_PAYROLL,
            split=SplitType.TRAIN,
            description="Legitimate split payroll: ₹55k base + ₹33k performance allowance sums to ₹88k net.",
            expected_findings=[
                {"finding_type": "CANDIDATE_SPLIT_PAYROLL", "severity": "LOW", "target_sum": 88000}
            ]
        ),
        PacketCaseDef(
            reference_number="LOAN-2026-TR04",
            applicant_name="Sneha Patel",
            employer_declared="HDFC Bank Ltd",
            employer_actual="HDFC Bank Ltd",
            pan_number="DFKPS7722D",
            loan_amount=1500000,
            gross_salary_declared=95000,
            net_salary_declared=76000,
            gross_salary_slip=95000,
            net_salary_slip=76000,
            bank_credits_monthly=[
                [{"amount": 45000, "narration": "ACH/SALARY/HDFC BANK", "date": "01-MAY-2026"}],
                [{"amount": 45000, "narration": "ACH/SALARY/HDFC BANK", "date": "01-JUN-2026"}],
                [{"amount": 45000, "narration": "ACH/SALARY/HDFC BANK", "date": "01-JUL-2026"}]
            ],
            scenario=ScenarioType.SALARY_INFLATION_MISMATCH,
            split=SplitType.TRAIN,
            description="Income discrepancy: Declares ₹76k net, bank only reflects ₹45k credit (gap of ₹31k).",
            expected_findings=[
                {"finding_type": "SALARY_INFLATION_DISCREPANCY", "severity": "HIGH", "delta": -31000}
            ]
        ),
        PacketCaseDef(
            reference_number="LOAN-2026-TR05",
            applicant_name="Mohammed Faizan",
            employer_declared="Wipro Enterprises Ltd",
            employer_actual="Alpha Logistics Pvt Ltd",
            pan_number="EGMPF3311E",
            loan_amount=3000000,
            gross_salary_declared=140000,
            net_salary_declared=110000,
            gross_salary_slip=140000,
            net_salary_slip=110000,
            bank_credits_monthly=[
                [{"amount": 110000, "narration": "NEFT/ALPHA LOGISTICS/SAL", "date": "01-MAY-2026"}],
                [{"amount": 110000, "narration": "NEFT/ALPHA LOGISTICS/SAL", "date": "01-JUN-2026"}],
                [{"amount": 110000, "narration": "NEFT/ALPHA LOGISTICS/SAL", "date": "01-JUL-2026"}]
            ],
            scenario=ScenarioType.EMPLOYER_ENTITY_MISMATCH,
            split=SplitType.TRAIN,
            description="Employer mismatch: Declares Wipro, but payslip and bank credit name Alpha Logistics.",
            expected_findings=[
                {"finding_type": "EMPLOYER_NAME_MISMATCH", "severity": "HIGH", "declared": "Wipro Enterprises Ltd", "found": "Alpha Logistics Pvt Ltd"}
            ]
        ),
        PacketCaseDef(
            reference_number="LOAN-2026-TR06",
            applicant_name="Kavita Deshmukh",
            employer_declared="Mahindra & Mahindra Ltd",
            employer_actual="Mahindra & Mahindra Ltd",
            pan_number="FHNPD4499F",
            loan_amount=2000000,
            gross_salary_declared=100000,
            net_salary_declared=82000,
            gross_salary_slip=100000,
            net_salary_slip=82000,
            bank_credits_monthly=[
                [{"amount": 82000, "narration": "ACH/SALARY/MAHINDRA", "date": "01-MAY-2026"}],
                [{"amount": 82000, "narration": "ACH/SALARY/MAHINDRA", "date": "01-JUN-2026"}],
                [{"amount": 82000, "narration": "ACH/SALARY/MAHINDRA", "date": "01-JUL-2026"}]
            ],
            scenario=ScenarioType.PROMPT_INJECTION_TEXT_LAYER,
            split=SplitType.TRAIN,
            description="Adversarial security check: White-on-white text layer prompt injection payload embedded.",
            expected_findings=[
                {"finding_type": "PROMPT_INJECTION_DETECTED", "severity": "CRITICAL"}
            ]
        ),

        # --- VAL SPLIT (2 Cases) ---
        PacketCaseDef(
            reference_number="LOAN-2026-VA01",
            applicant_name="Arjun V. Nair",
            employer_declared="Larsen & Toubro Infotech",
            employer_actual="Larsen & Toubro Infotech",
            pan_number="GIQPN6611G",
            loan_amount=2800000,
            gross_salary_declared=130000,
            net_salary_declared=105000,
            gross_salary_slip=130000,
            net_salary_slip=105000,
            bank_credits_monthly=[
                [{"amount": 105000, "narration": "ACH/SALARY/LTI INFOTECH", "date": "01-MAY-2026"}],
                [{"amount": 105000, "narration": "ACH/SALARY/LTI INFOTECH", "date": "01-JUN-2026"}],
                [{"amount": 105000, "narration": "ACH/SALARY/LTI INFOTECH", "date": "01-JUL-2026"}]
            ],
            scenario=ScenarioType.CLEAN_CONSISTENT,
            split=SplitType.VAL,
            description="Validation clean baseline case.",
            expected_findings=[]
        ),
        PacketCaseDef(
            reference_number="LOAN-2026-VA02",
            applicant_name="Ritu Singhania",
            employer_declared="Kotak Mahindra Prime",
            employer_actual="Kotak Mahindra Prime",
            pan_number="HJRPS8833H",
            loan_amount=2400000,
            gross_salary_declared=115000,
            net_salary_declared=92000,
            gross_salary_slip=115000,
            net_salary_slip=92000,
            bank_credits_monthly=[
                [{"amount": 92000, "narration": "ACH/SALARY/KOTAK PRIME", "date": "01-MAY-2026"}],
                [{"amount": 92000, "narration": "ACH/SALARY/KOTAK PRIME", "date": "01-JUN-2026"}],
                [{"amount": 92000, "narration": "ACH/SALARY/KOTAK PRIME", "date": "01-JUL-2026"}]
            ],
            scenario=ScenarioType.FONT_BASELINE_DISPLACEMENT,
            split=SplitType.VAL,
            description="Forensic baseline anomaly: Payslip Net Payable digit baseline is visibly displaced by 3.5px.",
            expected_findings=[
                {"finding_type": "FONT_BASELINE_ANOMALY", "severity": "MEDIUM", "displacement_px": 3.5}
            ]
        ),

        # --- TEST SPLIT (4 Cases - Held Out for Blind Benchmark) ---
        PacketCaseDef(
            reference_number="LOAN-2026-TE01",
            applicant_name="Aniket Paloi",
            employer_declared="Apex FinTech Labs Pvt Ltd",
            employer_actual="Apex FinTech Labs Pvt Ltd",
            pan_number="IKSPJ9911I",
            loan_amount=2000000,
            gross_salary_declared=90000,
            net_salary_declared=75000,
            gross_salary_slip=90000,
            net_salary_slip=75000,
            bank_credits_monthly=[
                [
                    {"amount": 42000, "narration": "ACH/SALARY/APEX FIN", "date": "01-MAY-2026"},
                    {"amount": 33000, "narration": "NEFT/INCENTIVE/APEX", "date": "03-MAY-2026"}
                ],
                [
                    {"amount": 42000, "narration": "ACH/SALARY/APEX FIN", "date": "01-JUN-2026"},
                    {"amount": 33000, "narration": "NEFT/INCENTIVE/APEX", "date": "03-JUN-2026"}
                ],
                [
                    {"amount": 42000, "narration": "ACH/SALARY/APEX FIN", "date": "01-JUL-2026"},
                    {"amount": 33000, "narration": "NEFT/INCENTIVE/APEX", "date": "03-JUL-2026"}
                ]
            ],
            scenario=ScenarioType.SALARY_INFLATION_MISMATCH,
            split=SplitType.TEST,
            description="Primary test dossier: Declares ₹90k gross / ₹75k net; bank reflects ₹42k primary + ₹33k delayed credit.",
            expected_findings=[
                {"finding_type": "SALARY_INFLATION_DISCREPANCY", "severity": "HIGH", "delta": -48000},
                {"finding_type": "CANDIDATE_SPLIT_PAYROLL", "severity": "LOW", "candidate_amount": 33000}
            ]
        ),
        PacketCaseDef(
            reference_number="LOAN-2026-TE02",
            applicant_name="Meera Joshi",
            employer_declared="Bharti Airtel Ltd",
            employer_actual="Bharti Airtel Ltd",
            pan_number="JLQPM7744J",
            loan_amount=2100000,
            gross_salary_declared=105000,
            net_salary_declared=84000,
            gross_salary_slip=105000,
            net_salary_slip=84000,
            bank_credits_monthly=[
                [{"amount": 84000, "narration": "ACH/SALARY/BHARTI AIRTEL", "date": "01-MAY-2026"}],
                [{"amount": 84000, "narration": "ACH/SALARY/BHARTI AIRTEL", "date": "01-JUN-2026"}],
                [{"amount": 84000, "narration": "ACH/SALARY/BHARTI AIRTEL", "date": "01-JUL-2026"}]
            ],
            scenario=ScenarioType.CLEAN_CONSISTENT,
            split=SplitType.TEST,
            description="Blind test clean benchmark case.",
            expected_findings=[]
        ),
        PacketCaseDef(
            reference_number="LOAN-2026-TE03",
            applicant_name="Vikramaditya Rao",
            employer_declared="Adani Ports & SEZ Ltd",
            employer_actual="Adani Ports & SEZ Ltd",
            pan_number="KMRPV1122K",
            loan_amount=3500000,
            gross_salary_declared=150000,
            net_salary_declared=120000,
            gross_salary_slip=150000,
            net_salary_slip=120000,
            bank_credits_monthly=[
                [{"amount": 120000, "narration": "ACH/SALARY/ADANI PORTS", "date": "01-MAY-2026"}],
                [{"amount": 120000, "narration": "ACH/SALARY/ADANI PORTS", "date": "01-JUN-2026"}],
                [{"amount": 120000, "narration": "ACH/SALARY/ADANI PORTS", "date": "01-JUL-2026"}]
            ],
            scenario=ScenarioType.BALANCE_RECONCILIATION_FAILURE,
            split=SplitType.TEST,
            description="Arithmetic ledger gap: May 2026 bank statement running balance fails reconciliation check by ₹50,000.",
            expected_findings=[
                {"finding_type": "BALANCE_ARITHMETIC_FAILURE", "severity": "HIGH", "discrepancy": 50000}
            ]
        ),
        PacketCaseDef(
            reference_number="LOAN-2026-TE04",
            applicant_name="Pooja Hegde",
            employer_declared="Flipkart Internet Pvt Ltd",
            employer_actual="Flipkart Internet Pvt Ltd",
            pan_number="LNQPH3355L",
            loan_amount=2600000,
            gross_salary_declared=125000,
            net_salary_declared=98000,
            gross_salary_slip=125000,
            net_salary_slip=98000,
            bank_credits_monthly=[
                [{"amount": 98000, "narration": "ACH/SALARY/FLIPKART", "date": "01-MAY-2026"}],
                [{"amount": 98000, "narration": "ACH/SALARY/FLIPKART", "date": "01-JUN-2026"}],
                [{"amount": 98000, "narration": "ACH/SALARY/FLIPKART", "date": "01-JUL-2026"}]
            ],
            scenario=ScenarioType.VARIABLE_BONUS_ROLLUP,
            split=SplitType.TEST,
            description="Consistent payroll with quarterly compensation rollup.",
            expected_findings=[]
        ),
    ]

def generate_all_packets_and_manifests(output_dir: str = "data") -> Dict[str, Any]:
    """Generates all 12 PDF packets on disk and outputs disjoint split manifests."""
    cases = get_12_curated_packet_definitions()
    
    packets_dir = os.path.join(output_dir, "fictional_packets")
    manifests_dir = os.path.join(output_dir, "manifests")
    os.makedirs(packets_dir, exist_ok=True)
    os.makedirs(manifests_dir, exist_ok=True)

    manifest_train = []
    manifest_val = []
    manifest_test = []
    ground_truth = {}

    for case in cases:
        case_dir = os.path.join(packets_dir, case.reference_number)
        os.makedirs(case_dir, exist_ok=True)

        # 1. Application form
        app_bytes = build_application_form(case)
        with open(os.path.join(case_dir, "application_form.pdf"), "wb") as f:
            f.write(app_bytes)

        # 2. 3 Salary slips
        slip_paths = []
        for m_idx in range(3):
            slip_bytes = build_salary_slip(case, m_idx)
            path = os.path.join(case_dir, f"salary_slip_m{m_idx + 1}.pdf")
            with open(path, "wb") as f:
                f.write(slip_bytes)
            slip_paths.append(path)

        # 3. Bank statement
        bank_bytes = build_bank_statement(case)
        bank_path = os.path.join(case_dir, "bank_statement_3mo.pdf")
        with open(bank_path, "wb") as f:
            f.write(bank_bytes)

        case_entry = {
            "reference_number": case.reference_number,
            "applicant_name": case.applicant_name,
            "declared_employer": case.employer_declared,
            "declared_gross": case.gross_salary_declared,
            "declared_net": case.net_salary_declared,
            "files": {
                "application": "application_form.pdf",
                "salary_slips": ["salary_slip_m1.pdf", "salary_slip_m2.pdf", "salary_slip_m3.pdf"],
                "bank_statement": "bank_statement_3mo.pdf"
            },
            "packet_directory": os.path.relpath(case_dir, start=os.getcwd()).replace("\\", "/"),
            "scenario": case.scenario.value,
            "description": case.description
        }

        if case.split == SplitType.TRAIN:
            manifest_train.append(case_entry)
        elif case.split == SplitType.VAL:
            manifest_val.append(case_entry)
        elif case.split == SplitType.TEST:
            manifest_test.append(case_entry)

        # Store ground truth with expected findings
        ground_truth[case.reference_number] = {
            "scenario": case.scenario.value,
            "expected_findings": case.expected_findings,
            "employer_actual": case.employer_actual,
            "net_salary_slip": case.net_salary_slip,
            "split": case.split.value
        }

    # Write manifests
    with open(os.path.join(manifests_dir, "train_manifest.json"), "w") as f:
        json.dump(manifest_train, f, indent=2)

    with open(os.path.join(manifests_dir, "val_manifest.json"), "w") as f:
        json.dump(manifest_val, f, indent=2)

    with open(os.path.join(manifests_dir, "test_manifest.json"), "w") as f:
        json.dump(manifest_test, f, indent=2)

    with open(os.path.join(manifests_dir, "ground_truth.json"), "w") as f:
        json.dump(ground_truth, f, indent=2)

    return {
        "total_cases": len(cases),
        "train_count": len(manifest_train),
        "val_count": len(manifest_val),
        "test_count": len(manifest_test),
        "output_directory": os.path.abspath(output_dir)
    }

if __name__ == "__main__":
    summary = generate_all_packets_and_manifests()
    print(f"Generated {summary['total_cases']} fictional loan packets successfully.")
    print(f"Train: {summary['train_count']} | Val: {summary['val_count']} | Test: {summary['test_count']}")

