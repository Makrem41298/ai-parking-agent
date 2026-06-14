from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from models.payment import PaymentStatus


class EventLogResponse(BaseModel):
    id: int
    paymentTransactionId: int
    status: str
    message: Optional[str]
    createdAt: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentTransactionResponse(BaseModel):
    id: int
    amount: Decimal
    paymentDateTime: Optional[datetime]
    method: str
    status: PaymentStatus
    paymentableId: int
    paymentableType: str
    createdAt: datetime
    updatedAt: datetime
    stripeSessionId: Optional[str]
    event_logs: List[EventLogResponse] = []

    model_config = ConfigDict(from_attributes=True)
