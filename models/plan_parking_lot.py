from sqlalchemy import Column, Integer, ForeignKey, Enum, DECIMAL
from sqlalchemy.orm import relationship

from database.__init__ import Base
from models.subscription import Subscription
from schemas.plan_parking_lot_schema import PlanStatus


class PlanParkingLot(Base):
    __tablename__ = "plan_parking_lots"

    id = Column(Integer, primary_key=True, index=True)
    planId = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    parkingLotId = Column(Integer, ForeignKey("parking_lots.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    status = Column(Enum(PlanStatus), default=PlanStatus.ACTIVE, nullable=False)
    renewFee = Column(DECIMAL(10, 2), nullable=False)
    subscriptionFee = Column(DECIMAL(10, 2), nullable=False)

    plan = relationship("Plan", back_populates="plan_parking_lots")
    parking_lot = relationship("ParkingLot", back_populates="plan_parking_lots")
    subscriptions = relationship("Subscription", back_populates="plan_parking_lot")