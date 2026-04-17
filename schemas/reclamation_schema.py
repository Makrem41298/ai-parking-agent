from enum import Enum
from pydantic import BaseModel, ConfigDict
from schemas.user_schemas import UserResponse


class ReclamationStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"


class ReclamationResponse(BaseModel):
    id: int
    clientId: int
    client: UserResponse
    adminId: int | None = None
    admin: UserResponse | None = None
    subject: str | None = None
    content: str
    solution: str | None = None
    status: ReclamationStatus = ReclamationStatus.IN_PROGRESS

    model_config = ConfigDict(from_attributes=True)

    def to_dict(self):
        return self.model_dump()

    def to_json(self):
        return self.model_dump_json(indent=2)



