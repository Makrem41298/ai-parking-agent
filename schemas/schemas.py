from pydantic import BaseModel, EmailStr
from models.Models import Role, AccountStatus


class UserResponse(BaseModel):
    id: int
    firstName: str
    lastName: str
    email: EmailStr
    phone: str
    CIN: str
    role: Role
    accountStatus: AccountStatus

    class Config:
        orm_mode = True