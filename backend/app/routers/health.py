from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.schemas.health import HealthResponse, CapabilitiesResponse

router = APIRouter(tags=["Health & Capabilities"])

@router.get("/health/live", response_model=HealthResponse)
def liveness():
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        details={"process": "alive"}
    )

@router.get("/health/ready", response_model=HealthResponse)
def readiness(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1;"))
        db_status = "connected"
    except Exception as e:
        db_status = f"unreachable: {str(e)}"
        
    return HealthResponse(
        status="ready" if db_status == "connected" else "unready",
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        details={
            "database": db_status,
            "storage_dir": str(settings.STORAGE_DIR),
            "storage_accessible": settings.STORAGE_DIR.exists()
        }
    )

@router.get("/capabilities", response_model=CapabilitiesResponse)
def capabilities():
    return CapabilitiesResponse(
        version=settings.VERSION,
        capabilities=settings.CAPABILITIES
    )

