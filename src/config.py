from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    prometheus_url: str
    log_level: str = "INFO"
    port: int = 8000
    vector_store_path: str
    model_name: str

    class Config:
        env_file = ".env"

settings = Settings()