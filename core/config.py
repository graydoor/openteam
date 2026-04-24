from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "openteam-agent-api"
    log_level: str = "INFO"
    run_timeout_sec: float = 12.0
    max_retries: int = 1
    max_output_chars: int = 1200
    model_config = SettingsConfigDict(
        env_prefix="OPENTEAM_",
        env_file=".env",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
