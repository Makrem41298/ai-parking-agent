from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class PlanStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"


class ActiveDay(BaseModel):
    day: str
    hoursInterval: str


class PlanResponse(BaseModel):
    id: int
    name: str
    activeDays: Optional[List[ActiveDay]] = None
    startDate: datetime
    endDate: datetime
    NumberOfBenefitDays: int
    model_config = ConfigDict(from_attributes=True)




