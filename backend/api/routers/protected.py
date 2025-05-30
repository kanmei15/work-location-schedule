from fastapi import APIRouter, Depends

from core.security import get_current_user
from models.user_model import User
from schemas.user_schema import UserResponse

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)

@router.get(
        "/me",
        summary="現在のログインユーザ情報の取得",
        description="ログインしているユーザ自身の情報（ID、メールアドレス、デフォルトパスワード使用中かどうか）を返します",
        response_description="現在のユーザ情報",
        response_model=UserResponse 
        )
def read_me(current_user: User = Depends(get_current_user)):
    return current_user
