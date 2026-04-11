from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict

from schemas.parking_lot_schema import ParkingLotResponse
from schemas.plan_schema import PlanResponse


class PlanStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"





class PlanParkingLotResponse(BaseModel):
    id: int
    planId: int
    plan: PlanResponse
    parkingLotId: int
    parking_lot: ParkingLotResponse
    status: PlanStatus = PlanStatus.ACTIVE
    renewFee: Decimal
    subscriptionFee: Decimal

    model_config = ConfigDict(from_attributes=True)