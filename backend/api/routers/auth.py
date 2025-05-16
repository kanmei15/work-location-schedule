import secrets

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config import settings
from core.security import create_access_token, create_refresh_token, get_current_user, pwd_context 
from db import get_db
from models.user_model import User

router = APIRouter()

# パスワード変更用のリクエストボディ
class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

# ログインエンドポイント
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # CSRFトークンを生成
    csrf_token = secrets.token_hex(32)

    # フロントが読み取れるように JSON に含めて返す
    response = JSONResponse(content={
        "message": "Login successful",
        "csrf_token": csrf_token,
        "is_default_password": user.is_default_password
    })

    # 本番環境では secure=True
    secure_cookie = settings.env == "production"

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

    return response

# ログアウトエンドポイント
@router.post("/logout")
def logout():
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response

# パスワード変更エンドポイント
@router.post("/change-password")
def change_password(request: PasswordChangeRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 現在のパスワードの確認
    if not pwd_context.verify(request.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    # 新しいパスワードをハッシュ化
    hashed_password = pwd_context.hash(request.new_password)

    # ユーザーのパスワードを更新
    current_user.hashed_password = hashed_password
    current_user.is_default_password = False

    db.commit()  # 変更をデータベースに保存

    return JSONResponse(content={"message": "Password updated successfully"})
