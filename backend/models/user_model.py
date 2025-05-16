from sqlalchemy import Boolean, Column, Integer, String
from db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    employee_number = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_default_password = Column(Boolean, default=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    commuting_allowance = Column(String, nullable=True)