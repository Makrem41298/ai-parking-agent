from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict

from schemas.parking_lot_schema import ParkingLotResponse
from schemas.user_schemas import UserResponse


class ReservationStatus(str, Enum):
    REQUESTED = "REQUESTED"
    CONFIRMED = "CONFIRMED"
    CANCELED = "CANCELED"
    EXPIRED = "EXPIRED"
    USED = "USED"



class ReservationResponse(BaseModel):
    id: int
    parkingLotId: int
    parking_lot:ParkingLotResponse
    userId: int
    client:UserResponse
    startTimeDate: datetime
    endTimeDate: datetime
    totalPrice: Decimal
    status: ReservationStatus
    entryTime: datetime | None
    leaveTime: datetime | None

    model_config = ConfigDict(from_attributes=True)