from pydantic import BaseModel
from enum import Enum

from schemas.tarif_grid_schemas import TarifGridResponse


class ParkingStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    MAINTENANCE = "MAINTENANCE"


class ParkingLotResponse(BaseModel):
    id: int
    name: str
    address: str
    city: str
    country: str
    covered: bool = False
    numberOfPlaces: int
    description: str | None = None
    statusParking: ParkingStatus = ParkingStatus.OPEN
    reservationAvailability: bool = True
    subscriptionAvailability: bool = True
    tarifGridId: int | None = None
    numberOfPlaceAvailable: int
    tarif_grid: TarifGridResponse | None

    class Config:
        orm_mode = True
