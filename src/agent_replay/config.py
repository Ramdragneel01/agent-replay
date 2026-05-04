"""Application settings (AR_ env prefix)."""
from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AR_", env_file=".env", extra="ignore")

    service_name: str = "agent-replay"
    host: str = "0.0.0.0"
    port: int = 8095
    log_level: str = "INFO"

    frontend_dir: str = "frontend"
    max_events_per_run: int = Field(5000, ge=10, le=50000)
