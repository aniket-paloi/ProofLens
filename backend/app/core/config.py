import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "ProofLens"
    VERSION: str = "0.2.0"
    API_PREFIX: str = "/api"
    SECRET_KEY: str = "prooflens-local-reviewer-secret-key-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    IS_VERCEL: bool = bool(os.environ.get("VERCEL"))
    REPO_ROOT: Path = Path(__file__).resolve().parent.parent.parent.parent
    BASE_DIR: Path = Path("/tmp/prooflens") if bool(os.environ.get("VERCEL")) else Path(__file__).resolve().parent.parent.parent.parent
    
    STORAGE_DIR: Path = (Path("/tmp/prooflens") if bool(os.environ.get("VERCEL")) else Path(__file__).resolve().parent.parent.parent.parent) / "storage"
    ORIGINALS_DIR: Path = (Path("/tmp/prooflens") if bool(os.environ.get("VERCEL")) else Path(__file__).resolve().parent.parent.parent.parent) / "storage" / "originals"
    DERIVATIVES_DIR: Path = (Path("/tmp/prooflens") if bool(os.environ.get("VERCEL")) else Path(__file__).resolve().parent.parent.parent.parent) / "storage" / "derivatives"
    REPORTS_DIR: Path = (Path("/tmp/prooflens") if bool(os.environ.get("VERCEL")) else Path(__file__).resolve().parent.parent.parent.parent) / "storage" / "reports"
    CHECKPOINTS_DIR: Path = (Path("/tmp/prooflens") if bool(os.environ.get("VERCEL")) else Path(__file__).resolve().parent.parent.parent.parent) / "storage" / "checkpoints"
    
    DATABASE_URL: str = f"sqlite:///{(Path('/tmp/prooflens') if bool(os.environ.get('VERCEL')) else Path(__file__).resolve().parent.parent.parent.parent) / 'prooflens.db'}"
    
    # Feature capabilities
    CAPABILITIES: dict = {
        "native_pdf_extraction": "implemented",
        "ocr_raster_extraction": "implemented",
        "financial_reconciliation": "implemented",
        "visual_forensics_baseline": "implemented",
        "region_classifier_mobilenet": "baseline",
        "bounded_investigation_agent": "implemented",
        "dossier_pdf_json": "implemented",
        "integrity_hash_chain": "implemented",
        "advanced_segmentation": "unsupported",
        "external_bank_verification": "unsupported"
    }

    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()

# Ensure directories exist
for path in [
    settings.STORAGE_DIR,
    settings.ORIGINALS_DIR,
    settings.DERIVATIVES_DIR / "pages",
    settings.DERIVATIVES_DIR / "crops",
    settings.REPORTS_DIR,
    settings.CHECKPOINTS_DIR,
]:
    path.mkdir(parents=True, exist_ok=True)

