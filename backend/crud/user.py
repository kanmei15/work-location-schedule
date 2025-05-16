from sqlalchemy.orm import Session
from sqlalchemy import extract, and_, not_, exists
from typing import Optional

from core.security import pwd_context
from models.user_model import User
from models.schedule_model import WorkSchedule

def create_user(db: Session, name: str) -> User:
    user = User(name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_all_users(db: Session):
    return db.query(User).all()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

# 対象月の勤務データが「未登録」のユーザー抽出
def get_users_missing_schedule(db: Session, year: int, month: int):
    users = db.query(User).filter(
        not_(
            exists().where(
                and_(
                    WorkSchedule.user_id == User.id,
                    extract('year', WorkSchedule.work_date) == year,
                    extract('month', WorkSchedule.work_date) == month,
                )
            )
        )
    ).all()
    return users

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def update_user_password(db: Session, user: User, new_password: str):
    user.hashed_password = pwd_context.hash(new_password)
    user.is_default_password = False
    db.commit()

def update_commuting_allowance(db: Session, user_id: int, allowance: str):
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.commuting_allowance = allowance
    db.commit()
    db.refresh(user)
    return user
