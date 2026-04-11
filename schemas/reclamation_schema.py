from enum import Enum
from pydantic import BaseModel, ConfigDict


class ReclamationStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"


class ReclamationResponse(BaseModel):
    id: int
    clientId: int
    adminId: int | None = None
    subject: str | None = None
    content: str
    solution: str | None = None
    status: ReclamationStatus = ReclamationStatus.IN_PROGRESS
    model_config = ConfigDict(from_attributes=True)


