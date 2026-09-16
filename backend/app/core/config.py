import os
from typing import List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: Union[str, List[str]] = "*"

    # Database
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = "autonomous_ops"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./autonomous_ops.db"
    )
    SEED_DATA: bool = True

    # AI Engine
    AI_ENGINE_URL: str = os.getenv("AI_ENGINE_URL", "http://localhost:8000")
    AI_ENGINE_TIMEOUT_SECONDS: float = float(os.getenv("AI_ENGINE_TIMEOUT_SECONDS", "15.0"))

    # Operations & Routing
    AVERAGE_SPEED_KMH: float = float(os.getenv("AVERAGE_SPEED_KMH", "30.0"))

    # SLA Default Limits (in hours)
    SLA_HOURS_CRITICAL: float = 2.0
    SLA_HOURS_HIGH: float = 4.0
    SLA_HOURS_MEDIUM: float = 8.0
    SLA_HOURS_LOW: float = 24.0

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [i.strip() for i in v.split(",") if i.strip()]
        return v


settings = Settings()
