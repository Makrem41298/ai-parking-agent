from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import  relationship

from  database.db import  Base
import enum

from schemas.user_schemas import AccountStatus, Role


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
    reservations=relationship("Reservation",back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    client_reclamations = relationship(
        "Reclamation",
        foreign_keys="Reclamation.clientId",
        back_populates="client",
        cascade="all, delete-orphan"
    )

    admin_reclamations = relationship(
        "Reclamation",
        foreign_keys="Reclamation.adminId",
        back_populates="admin"
    )