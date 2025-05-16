import os
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from api import schedules
from api import user
from api.routers import auth, protected
from config import Settings
from db import Base, engine

# 環境変数に応じて .env ファイルを動的に読み込む
env_file = ".env.production" if os.getenv("ENV") == "production" else ".env.development"
settings = Settings(_env_file=env_file)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)

# データベースの初期化
Base.metadata.create_all(bind=engine)

# Limiter の初期化（IPアドレス単位で制限）
limiter = Limiter(key_func=get_remote_address)

# FastAPIアプリケーションのインスタンス作成
app = FastAPI(
    debug=settings.debug,
    docs_url=None if not settings.debug else "/docs",
    redoc_url=None if not settings.debug else "/redoc",
    openapi_url=None if not settings.debug else "/openapi.json"
)

# CORSのミドルウェアを追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],  # すべてのHTTPメソッドを許可
    allow_headers=["*"],  # すべてのヘッダーを許可
)

# レート制限の追加
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: JSONResponse(
    status_code=429,
    content={"detail": "Rate limit exceeded"}
))
app.add_middleware(SlowAPIMiddleware)

# HTTPヘッダーの追加
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self' data:; "
            "connect-src 'self' " + settings.frontend_origin + "; "
            "frame-ancestors 'none';"
        )
        return response

if settings.env == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[settings.domain, "localhost", "127.0.0.1"]
    )
    app.add_middleware(SecurityHeadersMiddleware)

# ルーターをインクルード
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(protected.router, prefix="/api/auth", tags=["protected"])
app.include_router(user.router, prefix="/api")
app.include_router(schedules.router, prefix="/api")

# 全体にレート制限（例：すべてのルートで IP 毎に1分間に30回まで）
@app.middleware("http")
@limiter.limit("30/minute")
async def global_rate_limiter(request: Request, call_next):
    if request.url.path in ["/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)
    return await call_next(request)
