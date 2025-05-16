# api/schedule.py

import logging
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from core.security import get_current_user, verify_csrf_token
from db import SessionLocal
from crud import schedule as crud_schedule

logger = logging.getLogger(__name__)

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ScheduleRequest(BaseModel):
    user_id: int = Field(..., description="ユーザID")
    work_date: date = Field(..., description="勤務日（YYYY-MM-DD）")
    location: Optional[str] = Field(
        None,
        description=(
            "作業場所（例: '在' は在宅、'本' は本社など）\n"
            "空文字または null の場合、スケジュールは削除されます"
        )
    )

@router.post(
        "/schedules",
        dependencies=[Depends(verify_csrf_token)],
        summary="作業場所スケジュールの登録・更新",
        description=(
            "指定されたユーザの作業場所スケジュールを登録または更新します\n"
            "作業場所が空またはnullの場合は削除されます"
            ),
        response_description="登録・更新された作業場所スケジュール情報、または削除ステータスを返します"
        )
def add_or_update_schedule(data: ScheduleRequest, db: Session = Depends(get_db)):
    try:
        existing = crud_schedule.get_schedule(db, data.user_id, data.work_date)

        # location が null または空なら削除処理
        if data.location is None or data.location.strip() == "":
            if existing:
                crud_schedule.delete_schedule(db, existing)
                logger.info(f"Deleted schedule for user_id={data.user_id} on {data.work_date}")
            return {"status": "deleted"}

        # 登録または更新処理
        schedule = crud_schedule.save_schedule(db, data.user_id, data.work_date, data.location)
        logger.info(f"Saved schedule: {schedule}")
        return schedule

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB error in add_or_update_schedule: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")

    except Exception as e:
        logger.exception("Unexpected error in add_or_update_schedule")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")

@router.get(
        "/schedules",
        summary="作業場所スケジュールの取得",
        description=(
            "作業場所スケジュールを取得します\n"
            "オプションで `month` を指定することで、特定の月（例: '2025-05'）のスケジュールだけを取得できます\n"
            "取得されるデータには、ユーザID、勤務日、作業場所が含まれます"
            ),
        response_description="作業場所スケジュールのリストを返します"
        )
def list_schedules(month: Optional[str] = Query(None), db: Session = Depends(get_db)):
    try:
        results = crud_schedule.get_schedules_by_month(db, month)
        logger.info(f"Fetched {len(results)} schedules for month={month}")
        return results

    except SQLAlchemyError as e:
        logger.error(f"DB error in list_schedules: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")

    except Exception as e:
        logger.exception("Unexpected error in list_schedules")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")
