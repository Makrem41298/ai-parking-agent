from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship

from database.db import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    activeDays = Column(JSON, nullable=True, default=None)
    startDate = Column(DateTime, nullable=False)
    endDate = Column(DateTime, nullable=False)
    NumberOfBenefitDays = Column(Integer, nullable=False)
    plan_parking_lots = relationship("PlanParkingLot", back_populates="plan", cascade="all, delete-orphan")