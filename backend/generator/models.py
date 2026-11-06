from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

class ScenarioType(str, Enum):
    CLEAN_CONSISTENT = "CLEAN_CONSISTENT"
    LEGITIMATE_SPLIT_PAYROLL = "LEGITIMATE_SPLIT_PAYROLL"
    VARIABLE_BONUS_ROLLUP = "VARIABLE_BONUS_ROLLUP"
    SALARY_INFLATION_MISMATCH = "SALARY_INFLATION_MISMATCH"
    EMPLOYER_ENTITY_MISMATCH = "EMPLOYER_ENTITY_MISMATCH"
    PROMPT_INJECTION_TEXT_LAYER = "PROMPT_INJECTION_TEXT_LAYER"
    FONT_BASELINE_DISPLACEMENT = "FONT_BASELINE_DISPLACEMENT"
    BALANCE_RECONCILIATION_FAILURE = "BALANCE_RECONCILIATION_FAILURE"

class SplitType(str, Enum):
    TRAIN = "TRAIN"
    VAL = "VAL"
    TEST = "TEST"

@dataclass
class PacketCaseDef:
    reference_number: str
    applicant_name: str
    employer_declared: str
    employer_actual: str
    pan_number: str
    loan_amount: int
    gross_salary_declared: int
    net_salary_declared: int
    gross_salary_slip: int
    net_salary_slip: int
    bank_credits_monthly: List[List[Dict[str, Any]]] # 3 months of payroll credits
    scenario: ScenarioType
    split: SplitType
    description: str
    expected_findings: List[Dict[str, Any]] = field(default_factory=list)

