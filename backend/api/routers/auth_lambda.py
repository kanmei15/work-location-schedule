import logging
import secrets

from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from config import settings
from core.security import create_access_token, create_refresh_token
from crud import user as crud_user
from db import get_db
from models.user_model import User
from schemas.token_schema import LambdaLoginResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Lambdaからの呼び出しをAPIキーで制限するための依存関数
LAMBDA_API_KEY = settings.lambda_api_key  # .env などで管理推奨

def verify_lambda_api_key(x_api_key: str = Header(...)):
    if x_api_key != LAMBDA_API_KEY:
        logger.warning(f"Invalid API key attempted: {x_api_key}")
        raise HTTPException(status_code=403, detail="Forbidden: invalid API key")

@router.post(
    "/login/lambda",
    dependencies=[Depends(verify_lambda_api_key)],
    response_model=LambdaLoginResponse,
    summary="Lambda専用ログインAPI",
    description="Lambdaからの呼び出し専用。アクセストークン、リフレッシュトークン、CSRFトークンをJSONで返します。",
)
def login_for_lambda(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        user = crud_user.get_user_by_email(db, form_data.username)
        if not user or not crud_user.verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Failed lambda login attempt for email: {form_data.username}")
            raise HTTPException(status_code=401, detail="Invalid email or password")

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        csrf_token = secrets.token_hex(32)

        logger.info(f"Lambda login successful: id={user.id}, email={user.email}")

        return LambdaLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            csrf_token=csrf_token,
            is_default_password=user.is_default_password,
            message="Login successful"
        )

    except SQLAlchemyError as e:
        logger.error(f"Database error during lambda login: {e}")
        raise HTTPException(status_code=500, detail="Database error")

    except Exception as e:
        logger.error(f"Unexpected error during lambda login: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
