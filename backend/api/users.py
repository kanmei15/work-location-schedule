from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.security import get_current_user, verify_csrf_token
from db import SessionLocal
from models.user_model import User

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/users", dependencies=[Depends(verify_csrf_token)])
def create_user(name: str, db: Session = Depends(get_db)):
    user = User(name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/users")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()