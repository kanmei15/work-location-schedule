from pydantic import BaseModel, EmailStr
from typing import Optional

# ユーザの共通項目（ベース）
class UserBase(BaseModel):
    employee_number: str
    name: str
    email: EmailStr
    commuting_allowance: Optional[str] = None

# ユーザのレスポンス表示用（DBから取得したデータに使う）
class UserResponse(UserBase):
    id: int
    email: EmailStr
    is_default_password: bool

    class Config:
        orm_mode = True  # SQLAlchemyモデルと連携させるために必要

class AllowanceUpdate(BaseModel):
    allowance: str