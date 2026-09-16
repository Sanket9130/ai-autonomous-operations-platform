"""
FastAPI Backend Application for AI Autonomous Operations Platform.
Orchestrates PostgreSQL/SQLite business data, inventory, and technician routing with the AI Engine.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.core.database import SessionLocal, init_db
from backend.app.seed.seed_data import seed_database
from backend.app.routers import assets, inventory, operations, technicians


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    init_db()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Facility Operations Backend API",
    description="Backend Orchestration Service connecting Database and AI Decision Intelligence Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration
allowed_origins = settings.CORS_ORIGINS
if isinstance(allowed_origins, str):
    if allowed_origins.strip() == "*":
        allowed_origins = ["*"]
    else:
        allowed_origins = [o.strip() for o in allowed_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(operations.router)
app.include_router(assets.router)
app.include_router(inventory.router)
app.include_router(technicians.router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Backend service health check."""
    return {
        "status": "healthy",
        "service": "backend-orchestrator",
        "version": "1.0.0",
        "ai_engine_target": settings.AI_ENGINE_URL,
    }


# Mount Frontend static files for unified single-server deployment
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dist.exists() and (frontend_dist / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
