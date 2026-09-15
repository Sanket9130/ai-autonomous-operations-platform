"""
FastAPI Backend Application for AI Autonomous Operations Platform.
Orchestrates PostgreSQL/SQLite business data, inventory, and technician routing with the AI Engine.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.database import init_db
from backend.app.routers import assets, inventory, operations, technicians


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    init_db()
    yield


app = FastAPI(
    title="Facility Operations Backend API",
    description="Backend Orchestration Service connecting Database and AI Decision Intelligence Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Dynamic CORS Configuration
cors_origins_env = settings.CORS_ORIGINS
if cors_origins_env.strip() == "*":
    allowed_origins = ["*"]
else:
    allowed_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pathlib import Path
from fastapi.staticfiles import StaticFiles

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

