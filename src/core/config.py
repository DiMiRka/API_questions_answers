import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()
env_path = Path(".env.docker" if os.getenv("DOCKER_MODE") == "1" else ".env")
load_dotenv(env_path)


class AppSettings(BaseSettings):
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", env="POSTGRES_PASSWORD")
    postgres_host: str = Field(default="db", env="POSTGRES_HOST")
    postgres_port: str = Field(default="5432", env="POSTGRES_PORT")
    postgres_db: str = Field(default="Pereval", env="POSTGRES_DB")

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    host: str = Field(default="localhost", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=True, env="RELOAD")

    class Config:
        _env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


app_settings = AppSettings()


uvicorn_options = {
    "host": app_settings.host,
    "port": app_settings.port,
    "reload": app_settings.reload,
}
