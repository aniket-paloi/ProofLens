from typing import Dict, Any
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    details: Dict[str, Any] = {}

class CapabilitiesResponse(BaseModel):
    version: str
    capabilities: Dict[str, str]

