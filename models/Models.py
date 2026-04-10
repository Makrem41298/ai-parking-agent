from sqlalchemy import Column, Integer, String, Enum
from  database.db import  Base
import enum

class AccountStatus(str, enum.Enum):
    ACTIVE = "ACTIVE",
    BLOCKED = "BLOCKED",
    PENDING = "PENDING",

class Role(str, enum.Enum):
    CLIENT = "CLIENT",
    ADMIN = "ADMIN",
    SUPER_ADMIN = "SUPER_ADMIN",

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    firstName = Column(String(100), nullable=False)
    lastName = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    accountStatus = Column(Enum(AccountStatus), default=AccountStatus.ACTIVE)
    role = Column(Enum(Role), default=Role.CLIENT)
    CIN = Column(String(50), nullable=False)