from datetime import date
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from core.security import get_current_user, verify_csrf_token
from db import SessionLocal
from models.schedule_model import WorkSchedule

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
    user_id: int
    work_date: date
    location: Optional[str]  # null も許容するようにする

@router.post("/schedules", dependencies=[Depends(verify_csrf_token)])
###@router.post("/schedules")
def add_or_update_schedule(data: ScheduleRequest, db: Session = Depends(get_db)):
    schedule = db.query(WorkSchedule).filter_by(user_id=data.user_id, work_date=data.work_date).first()

    # ✅ location が null または空文字なら該当レコードを削除
    if data.location is None or data.location.strip() == '':
        if schedule:
            db.delete(schedule)
            db.commit()
        return {"status": "deleted"}

    # 通常の登録・更新
    if schedule:
        schedule.location = data.location
    else:
        schedule = WorkSchedule(user_id=data.user_id, work_date=data.work_date, location=data.location)
        db.add(schedule)

    db.commit()
    db.refresh(schedule)
    return schedule

@router.get("/schedules")
def list_schedules(month: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(WorkSchedule)
    if month:
        query = query.filter(WorkSchedule.work_date.like(f"{month}-%"))
    return query.all()
