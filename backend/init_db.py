from db import engine, Base, SessionLocal
from models.user_model import User
from datetime import date
from passlib.context import CryptContext

# パスワードハッシュ化用コンテキスト
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# テーブル作成
Base.metadata.create_all(bind=engine)

# ダミーデータの挿入
db = SessionLocal()

# ユーザーがまだいなければ挿入
if not db.query(User).first():

    hashed_pw = pwd_context.hash("password123")  # 任意の初期パスワード

    user1 = User(
        employee_number="1001",
        hashed_password=hashed_pw,
        name="佐藤",
        email="sato@test.co.jp",
        commuting_allowance="申請"
    )
    user2 = User(
        employee_number="1002",
        hashed_password=hashed_pw,
        name="鈴木",
        email="suzuki@test.co.jp",
        commuting_allowance="停止"
    )
    user3 = User(
        employee_number="1003",
        hashed_password=hashed_pw,
        name="佐野",
        email="hiro-sano@foresight.co.jp",
        commuting_allowance="申請"
    )
    db.add_all([user1, user2, user3])
    db.commit()

    # ユーザーIDを取得して勤務スケジュールを追加（例）
    db.refresh(user1)
    db.refresh(user2)

    #schedule1 = WorkSchedule(user_id=user1.id, work_date=date(2025, 5, 1), location="東京")
    #schedule2 = WorkSchedule(user_id=user2.id, work_date=date(2025, 5, 2), location="大阪")
    #db.add_all([schedule1, schedule2])
    db.commit()

db.close()