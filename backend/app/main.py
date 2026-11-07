from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import engine, Base
import backend.app.models  # Register all models with Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite tables and storage on startup
    if getattr(settings, "IS_VERCEL", False):
        try:
            import shutil
            tmp_db = settings.BASE_DIR / "prooflens.db"
            repo_db = settings.REPO_ROOT / "prooflens.db"
            if repo_db.exists() and not tmp_db.exists():
                shutil.copy2(str(repo_db), str(tmp_db))
            
            repo_storage = settings.REPO_ROOT / "storage"
            if repo_storage.exists() and not (settings.STORAGE_DIR / "originals").exists():
                shutil.copytree(str(repo_storage), str(settings.STORAGE_DIR), dirs_exist_ok=True)
        except Exception:
            pass

    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Evidence-Driven Document Investigation Workspace",
    lifespan=lifespan
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.app.routers import health, cases, runs, reviews, audit, extensions

app.include_router(health.router)
app.include_router(cases.router, prefix=settings.API_PREFIX)
app.include_router(cases.page_router, prefix=settings.API_PREFIX)
app.include_router(cases.page_router)  # Allow direct /documents access as well
app.include_router(runs.router, prefix=settings.API_PREFIX)
app.include_router(reviews.router, prefix=settings.API_PREFIX)
app.include_router(audit.router, prefix=settings.API_PREFIX)
app.include_router(extensions.router, prefix=settings.API_PREFIX)

frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {
            "app": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "tagline": "Don't Just Verify Documents. Investigate the Evidence.",
            "docs_url": "/docs",
            "health_url": "/health/ready"
        }

