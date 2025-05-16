import logging
import secrets

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from config import settings
from core.security import create_access_token, create_refresh_token, get_current_user, pwd_context 
from crud import user as crud_user
from db import get_db
from models.user_model import User

logger = logging.getLogger(__name__)

router = APIRouter()

# パスワード変更用のリクエストボディ
class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

# ログインエンドポイント
@router.post(
        "/login",
        summary="ログイン",
        description="ユーザ認証を行い、アクセストークン、リフレッシュトークン、CSRFトークンを返します",
        response_description="ログイン成功時にトークンとステータスを返します"
        )
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = crud_user.get_user_by_email(db, form_data.username)
        if not user or not crud_user.verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Failed login attempt for email: {form_data.username}")
            raise HTTPException(status_code=401, detail="Invalid email or password")

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        csrf_token = secrets.token_hex(32) # CSRFトークンを生成
        secure_cookie = settings.env == "production"

        # フロントが読み取れるように JSON に含めて返す
        response = JSONResponse(content={
            "message": "Login successful",
            "csrf_token": csrf_token,
            "is_default_password": user.is_default_password
        })

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=secure_cookie,
            samesite="Lax",
            max_age=60 * 15  # 15分
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=secure_cookie,
            samesite="Lax",
            max_age=60 * 60 * 24 * 7  # 7日
        )

        # CSRFトークンは JavaScript から読めるように HttpOnly=False で保存
        response.set_cookie(
            key="csrf_token",
            value=csrf_token,
            httponly=False,  # JavaScriptからアクセス可能
            secure=secure_cookie,
            samesite="Lax",
            max_age=60 * 15
        )

        logger.info(f"User login successful: id={user.id}, email={user.email}")
        return response

    except SQLAlchemyError as e:
        logger.error(f"Database error during login: {e}")
        raise HTTPException(status_code=500, detail="Database error")

    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ログアウトエンドポイント
@router.post(
        "/logout",
        summary="ログアウト",
        description="アクセストークンおよびリフレッシュトークンのクッキーを削除してログアウトします",
        response_description="ログアウト成功のメッセージを返します"
        )
def logout():
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    logger.info("User logged out")
    return response

@router.post(
        "/change-password",
        summary="パスワード変更",
        description="現在のパスワードを検証し、新しいパスワードに更新します",
        response_description="パスワード更新結果のメッセージを返します"
        )
def change_password(
    request: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        if not crud_user.verify_password(request.old_password, current_user.hashed_password):
            logger.warning(f"Password change failed (incorrect old password): user_id={current_user.id}")
            raise HTTPException(status_code=400, detail="Old password is incorrect")

        crud_user.update_user_password(db, current_user, request.new_password)
        logger.info(f"Password changed successfully: user_id={current_user.id}")
        return JSONResponse(content={"message": "Password updated successfully"})

    except SQLAlchemyError as e:
        logger.error(f"Database error during password change: {e}")
        raise HTTPException(status_code=500, detail="Database error")

    except Exception as e:
        logger.error(f"Unexpected error during password change: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")