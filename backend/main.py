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
from api.routers import auth, auth_lambda, protected
from config import settings
from db import Base, engine

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
logging.info(f"Frontend origin: {settings.frontend_origin}")

# レート制限の追加
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: JSONResponse(
    status_code=429,
    content={"detail": "Rate limit exceeded"}
))
app.add_middleware(SlowAPIMiddleware)

if settings.env == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[settings.domain]
    )

# ルーターをインクルード
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(auth_lambda.router, prefix="/api/auth", tags=["auth_lambda"])
app.include_router(protected.router, prefix="/api/auth", tags=["protected"])
app.include_router(user.router, prefix="/api")
app.include_router(schedules.router, prefix="/api")

# 全体にレート制限（例：すべてのルートで IP 毎に1分間に30回まで）
#@app.middleware("http")
#async def global_rate_limiter(request: Request, call_next):
#    if request.url.path in ["/docs", "/openapi.json", "/redoc"]:
#        return await call_next(request)
#    return await (call_next)(request)
#    #return await limiter.limit("30/minute")(call_next)(request)
