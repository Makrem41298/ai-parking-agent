from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict

from schemas.plan_parking_lot_schema import PlanParkingLotResponse
from schemas.user_schemas import UserResponse


class SubscriptionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    EXPIRED = "EXPIRED"
    CANCELED = "CANCELED"


class SubscriptionResponse(BaseModel):
    id: int
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    planParkingLotId: int
    plan_parking_lot:PlanParkingLotResponse
    userId: int
    user:UserResponse
    startDate: datetime
    endDate: datetime
    model_config = ConfigDict(from_attributes=True)


