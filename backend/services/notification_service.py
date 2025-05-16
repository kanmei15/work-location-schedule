import numpy as np

from datetime import date

from crud.user import get_users_missing_schedule
from db import SessionLocal
from utils.email_service import send_email

def is_past_3_business_days(from_date: date) -> bool:
    today = date.today()
    return np.busday_count(from_date.isoformat(), today.isoformat()) >= 3

def notify_users_missing_schedule():
    today = date.today()
    first_day = date(today.year, today.month, 1)

    if not is_past_3_business_days(first_day):
        return

    db = SessionLocal()
    users = get_users_missing_schedule(db, today.year, today.month)

    for user in users:
        if user.email:
            send_email(
                to=user.email,
                subject="作業場所スケジュールが未登録です",
                body=f"{today.month}月の作業場所スケジュールが登録されていません。至急ご対応ください。"
            )
