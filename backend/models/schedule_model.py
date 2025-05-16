from sqlalchemy import Column, Integer, String, Date, ForeignKey
from db import Base

class WorkSchedule(Base):
    __tablename__ = "work_schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    work_date = Column(Date, nullable=False)
    location = Column(String, nullable=False)