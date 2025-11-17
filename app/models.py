from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text
from sqlalchemy.sql import func
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    CLIENT = "client"
    EMPLOYEE = "employee"
    INVESTOR = "investor"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    company_name = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default=UserRole.CLIENT.value)
    user_metadata = Column("metadata", JSON, nullable=True, default={})
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)

