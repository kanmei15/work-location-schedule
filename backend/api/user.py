# api/user.py

import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from core.security import get_current_user, verify_csrf_token
from db import SessionLocal
from crud import user as crud_user

logger = logging.getLogger(__name__)

class AllowanceUpdate(BaseModel):
    allowance: str

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
        "/users",
        dependencies=[Depends(verify_csrf_token)],
        summary="新規ユーザの作成",
        description="指定された名前で新しいユーザを作成します",
        response_description="作成されたユーザ情報を返します"
        )
def create_user(name: str, db: Session = Depends(get_db)):
    try:
        user = crud_user.create_user(db, name)
        logger.info(f"Created user: id={user.id}, name={user.name}")
        return user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB error in create_user: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.exception("Unexpected error in create_user")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")

@router.get(
        "/users",
        summary="全ユーザの一覧取得",
        description="登録されている全ユーザの一覧を取得します",
        response_description="ユーザ情報のリストを返します"
        )
def list_users(db: Session = Depends(get_db)):
    try:
        users = crud_user.get_all_users(db)
        logger.info(f"Fetched {len(users)} users")
        return users
    except SQLAlchemyError as e:
        logger.error(f"DB error in list_users: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.exception("Unexpected error in list_users")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")

@router.patch(
        "/users/{user_id}/commuting_allowance",
        dependencies=[Depends(verify_csrf_token)],
        summary="通勤手当の更新",
        description="指定されたユーザの通勤手当の状態（申請・停止・不要など）を更新します",
        response_description="更新の結果メッセージを返します"
        )
def update_commuting_allowance(user_id: int, allowance_update: AllowanceUpdate, db: Session = Depends(get_db)):
    try:
        logger.debug(f"Received allowance (raw): {repr(allowance_update.allowance)}")
        user = crud_user.update_commuting_allowance(db, user_id, allowance_update.allowance)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"Updated commuting_allowance for user_id={user_id} to {allowance_update.allowance}")
        return {"message": "Updated successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB error in update_commuting_allowance: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.exception("Unexpected error in update_commuting_allowance")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")

@router.get(
    "/users/missing-schedule",
    dependencies=[], # ここだけヘッダー認証とする（lambdaから実行するため）
    summary="スケジュール未登録ユーザの取得",
    description="指定された年月に勤務スケジュールが未登録のユーザを取得します",
    response_description="未登録ユーザのリストを返します"
)
def get_users_missing_schedule(year: int, month: int, db: Session = Depends(get_db)):
    try:
        users = crud_user.get_users_missing_schedule(db, year, month)
        logger.info(f"{year}年{month}月の未登録ユーザー数: {len(users)}")
        return users
    except SQLAlchemyError as e:
        logger.error(f"DB error in get_users_missing_schedule: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.exception("Unexpected error in get_users_missing_schedule")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")
