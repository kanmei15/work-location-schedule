import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent  # 例えば backend ディレクトリ

class Settings(BaseSettings):
    env: str = "development"
    debug: bool = False
    domain: str = "localhost"

    frontend_origin: str

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "db"
    postgres_port: int = 5432

    secret_key: str = "your-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 60 * 24 * 7  # 7日

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / f".env.{os.getenv('ENV', 'development')}"),
        #env_file=f".env.{os.getenv('ENV', 'development')}",
        env_file_encoding="utf-8"
    )

settings = Settings()
