from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class AgentToolCallRecord:
    tool_name: str
    arguments: Dict[str, Any]
    result: Dict[str, Any]
    timestamp: str
    duration_ms: int

@dataclass
class InvestigationSessionState:
    case_id: str
    run_id: str
    status: str = "IN_PROGRESS" # IN_PROGRESS, COMPLETED, QUARANTINED, FAILED
    step_count: int = 0
    max_steps: int = 7
    quarantined: bool = False
    quarantine_reason: Optional[str] = None
    tool_history: List[AgentToolCallRecord] = field(default_factory=list)
    findings_reviewed: List[str] = field(default_factory=list)
    recommended_disposition: Optional[str] = None
    disposition_justification: Optional[str] = None
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None

