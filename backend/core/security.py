import logging

from datetime import datetime, timedelta, timezone
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Optional

from config import settings
from crud.user import get_user_by_id
from db import get_db
from models.user_model import User

# ロガー設定
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# トークン生成（共通）
def create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    
    logger.debug(f"Token created for sub={data.get('sub')} with expiry={expire}")
    return token

def create_access_token(user_id: int) -> str:
    return create_token(
        {"sub": str(user_id), "type": "access"},
        timedelta(minutes=settings.access_token_expire_minutes)
    )

def create_refresh_token(user_id: int) -> str:
    return create_token(
        {"sub": str(user_id), "type": "refresh"},
        timedelta(minutes=settings.refresh_token_expire_minutes)
    )

# トークン検証（直接使用されることは少ない）
def decode_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

        logger.debug("Token decoded successfully")
        return payload.get("sub")

    except JWTError as e:
        logger.warning(f"Failed to decode token: {e}")
        return None

async def verify_csrf_token(request: Request):
    csrf_cookie = request.cookies.get("csrf_token")
    csrf_header = request.headers.get("X-CSRF-Token")

    if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
        logger.warning("CSRF token mismatch")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token mismatch")
    
    logger.debug("CSRF token verified successfully")

# 認証付きルート用：現在のユーザーを取得
async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:

    auth_header: Optional[str] = request.headers.get("Authorization")
    token: Optional[str] = None

    # Authorization ヘッダーをチェック
    if auth_header and auth_header.startswith("Bearer "):
        # ヘッダーに "Bearer <token>" があればそれを使う
        token = auth_header[len("Bearer ") :].strip()
        logger.debug("Using token from Authorization header")
    else:
        # ヘッダーがなければ、Cookie の access_token をチェック
        cookie_token = request.cookies.get("access_token")
        if cookie_token:
            token = cookie_token
            logger.debug("Using token from access_token cookie")

    if not token:
        logger.warning("Missing access token in request cookies")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # トークンをデコードして user_id を取り出す
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")

        if user_id is None:
            logger.warning("Access token is missing 'sub' claim")
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

    # DB からユーザを取得
    user = get_user_by_id(db, int(user_id))
    if not user:
        logger.warning(f"User not found: user_id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    logger.debug(f"Authenticated user: id={user.id}, email={user.email}")
    return user