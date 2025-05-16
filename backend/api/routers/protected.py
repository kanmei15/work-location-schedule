from fastapi import APIRouter, Depends

from core.security import get_current_user
from models.user_model import User

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)

@router.get(
        "/me",
        summary="現在のログインユーザ情報の取得",
        description="ログインしているユーザ自身の情報（ID、メールアドレス、デフォルトパスワード使用中かどうか）を返します",
        response_description="現在のユーザ情報"
        )
def read_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_default_password": current_user.is_default_password
    }
