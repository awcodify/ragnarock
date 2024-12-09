# src/config.py
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    prometheus_url: str = "http://localhost:9090"
    log_level: str = "INFO"
    port: int = 8000
    vector_store_path: str = "data/vector_store"
    llm_gateway_url: str = "http://localhost:3000"

    model_config = ConfigDict(env_file=".env", extra="allow")  # Allow extra fields


settings = Settings()

__all__ = ["settings"]
