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

    #smtp_host: str = "smtp.gmail.com"      # SMTPサーバのホスト名（例: smtp.gmail.com）
    #smtp_port: int = 587                     # SMTPサーバのポート番号（STARTTLSなら通常587）
    #smtp_user: str = "your-email@example.com"  # SMTP認証に使うメールアドレス（送信元メール）
    #smtp_password: str = "your_password"    # SMTP認証に使うパスワード

    lambda_api_key: str = "your-lambda-apy-key"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / f".env.{os.getenv('ENV', 'development')}"),
        env_file_encoding="utf-8"
    )

settings = Settings()
