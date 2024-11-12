# src/config.py
from enum import Enum
from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings

class LLMProvider(str, Enum):
    CLAUDE = "claude"
    GPT = "gpt"

class Settings(BaseSettings):
    prometheus_url: str = "http://localhost:9090"
    log_level: str = "INFO"
    port: int = 8000
    vector_store_path: str = "data/vector_store"
    
    # LLM settings
    llm_provider: LLMProvider = Field(default=LLMProvider.CLAUDE)
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    claude_model: str = "claude-3-sonnet-20240229"
    gpt_model: str = "gpt-3.5-turbo"

    model_config = ConfigDict(
        env_file=".env",
        extra="allow"  # Allow extra fields
    )

settings = Settings()

__all__ = ['settings', 'LLMProvider']