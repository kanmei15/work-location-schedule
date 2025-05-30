from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class ScheduleBase(BaseModel):
    user_id: int = Field(..., description="ユーザID")
    work_date: date = Field(..., description="勤務日（YYYY-MM-DD）")
    location: Optional[str] = Field(
        None,
        description=(
            "作業場所（例: '在' は在宅、'本' は本社など）\n"
            "空文字または null の場合、スケジュールは削除されます"
        )
    )

class ScheduleRequest(ScheduleBase):
    pass

class ScheduleResponse(ScheduleBase):
    id: int

    class Config:
        orm_mode = True
