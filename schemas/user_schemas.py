import enum
from pydantic import BaseModel, EmailStr, ConfigDict

class AccountStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    PENDING = "PENDING"

class Role(str, enum.Enum):
    CLIENT = "CLIENT"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


class UserResponse(BaseModel):
    id: int
    firstName: str
    lastName: str
    email: EmailStr
    phone: str
    role: Role
    accountStatus: AccountStatus

    model_config = ConfigDict(from_attributes=True)