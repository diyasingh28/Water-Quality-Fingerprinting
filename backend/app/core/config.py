from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    database_url: str = "sqlite:///./water_quality.db"
    cors_origins: str = "http://localhost:3000"
    model_dir: str = "./ml_artifacts"
    env: str = "development"

    class Config:
        env_file = ".env"

    @property
    def cors_origin_list(self):
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def model_dir_path(self) -> Path:
        return Path(self.model_dir)


settings = Settings()
