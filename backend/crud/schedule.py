from datetime import date
from sqlalchemy.orm import Session
from typing import Optional, List

from models.schedule_model import WorkSchedule

def get_schedule(db: Session, user_id: int, work_date: date) -> Optional[WorkSchedule]:
    return db.query(WorkSchedule).filter_by(user_id=user_id, work_date=work_date).first()

def delete_schedule(db: Session, schedule: WorkSchedule):
    db.delete(schedule)
    db.commit()

def save_schedule(db: Session, user_id: int, work_date: date, location: str) -> WorkSchedule:
    schedule = get_schedule(db, user_id, work_date)
    if schedule:
        schedule.location = location
    else:
        schedule = WorkSchedule(user_id=user_id, work_date=work_date, location=location)
        db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule

def get_schedules_by_month(db: Session, month: Optional[str]) -> List[WorkSchedule]:
    query = db.query(WorkSchedule)
    if month:
        query = query.filter(WorkSchedule.work_date.like(f"{month}-%"))
    return query.all()
