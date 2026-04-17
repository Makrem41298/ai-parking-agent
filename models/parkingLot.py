from sqlalchemy import Column, Integer, String, Boolean, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship, Session
from database.__init__ import Base
from schemas.parking_lot_schema import ParkingStatus





class ParkingLot(Base):
    __tablename__ = "parking_lots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)

    covered = Column(Boolean, default=False)
    numberOfPlaces = Column(Integer, nullable=False)
    numberOfPlaceAvailable = Column(Integer, default=0)

    description = Column(Text, nullable=True)

    statusParking = Column(
        Enum(ParkingStatus),
        default=ParkingStatus.OPEN,
        nullable=False
    )

    reservationAvailability = Column(Boolean, default=True)
    subscriptionAvailability = Column(Boolean, default=True)

    tarifGridId = Column(
        Integer,
        ForeignKey("tariff_grids.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True
    )

    # Relationship
    tarif_grid = relationship("TarifGrid", back_populates="parking_lots")
    reservations=relationship("Reservation",back_populates="parking_lot")
    plan_parking_lots = relationship("PlanParkingLot", back_populates="parking_lot")