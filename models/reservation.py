from sqlalchemy import Column, Integer, ForeignKey, Date, DECIMAL, Enum
from sqlalchemy.orm import relationship

from database.__init__ import Base
from schemas.reservation_schema import ReservationStatus


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    parkingLotId = Column(Integer, ForeignKey("parking_lots.id", ondelete="CASCADE"), nullable=False)
    userId = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    startTimeDate = Column(Date, nullable=False)
    endTimeDate = Column(Date, nullable=False)
    totalPrice = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(ReservationStatus), default=ReservationStatus.REQUESTED, nullable=False)
    entryTime = Column(Date, nullable=True)
    leaveTime = Column(Date, nullable=True)

    parking_lot = relationship("ParkingLot", back_populates="reservations")
    client = relationship("User", back_populates="reservations")