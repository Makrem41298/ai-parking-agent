from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship

from database.__init__ import Base
from models.parkingLot import ParkingLot


class TarifGrid (Base):
    __tablename__="tariff_grids"
    id= Column(Integer,primary_key=True,index=True)
    name=Column(String(100),nullable=False)
    grid=Column(JSON,nullable=False)
    parking_lots = relationship("ParkingLot", back_populates="tarif_grid")