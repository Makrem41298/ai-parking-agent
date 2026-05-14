from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship

from database.__init__ import Base
from models.user import User
from schemas.subscription_schema import SubscriptionStatus


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False)
    planParkingLotId = Column(
        Integer,
        ForeignKey("plan_parking_lots.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    userId = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    startDate = Column(DateTime, nullable=False)
    endDate = Column(DateTime, nullable=False)

    plan_parking_lot = relationship("PlanParkingLot", back_populates="subscriptions")
    user = relationship("User", back_populates="subscriptions")