"""
Backend Application Configuration.
Reads settings from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class Settings:
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    PORT: int = int(os.getenv("PORT", "5000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    # AI Engine Endpoint
    AI_ENGINE_URL: str = os.getenv("AI_ENGINE_URL", "http://localhost:8000/autonomous-operation")
    AI_ENGINE_TIMEOUT_SECONDS: float = float(os.getenv("AI_ENGINE_TIMEOUT_SECONDS", "10.0"))

    # Database Path / Connection
    DATABASE_PATH: Path = Path(__file__).resolve().parent.parent / "facility_operations.db"

    # CORS
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:5173",
    )


settings = Settings()
