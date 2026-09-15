import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.database import init_db, SessionLocal
from backend.app.seed.seed_data import seed_database
from backend.app.api import api_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("autonomous_ops")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    logger.info("Initializing database schema...")
    init_db()

    # Seed initial test data
    db = SessionLocal()
    try:
        logger.info("Verifying seed data...")
        seed_database(db)
    finally:
        db.close()

    yield
    logger.info("Shutting down autonomous operations platform...")


app = FastAPI(
    title="AI Autonomous Operations Intelligence Platform",
    description="Backend orchestration for autonomous industrial asset operations, routing, technician assignment, and SLA tracking.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
origins = settings.CORS_ORIGINS
if isinstance(origins, str):
    origins = [origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health checks
@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "autonomous-operations-backend",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


# Include all REST API routes
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
