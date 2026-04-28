from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SaleAgents API"
    app_env: str = "local"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    api_prefix: str = "/api/v1"
    frontend_origins: str = "http://localhost:8081,http://47.85.54.50:8081"
    secret_key: str = "saleagents-secret-key-change-in-production"
    access_token_expire_minutes: int = 60 * 24  # 1 day
    refresh_token_expire_days: int = 7
    llm_ready: bool = False
    llm_model: str = "glm-4"
    llm_timeout_seconds: int = 300
    llm_base_url: str | None = None
    llm_api_key: str | None = None
    llm_max_review_issues: int = 5

    database_url_override: str | None = None
    storage_path: str | None = None

    # SQLite for backend-v2
    @property
    def database_url(self) -> str:
        if self.database_url_override:
            return self.database_url_override
        # Ensure database is created in the project root of backend-v2
        db_path = Path(__file__).resolve().parents[2] / "sale_agents_v2.db"
        return f"sqlite:///{db_path}"

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.frontend_origins.split(",") if item.strip()]

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
