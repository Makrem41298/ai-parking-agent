
from sqlalchemy.orm import Session
from models.user import User
from schemas.user_schemas import UserResponse


def filter_users(db: Session, filters: dict,skip: int = 0,limit: int = 20):
    query = db.query(User)

    if filters.get("id") is not None:
        query = query.filter(User.id == filters["id"])

    if filters.get("firstName"):
        query = query.filter(User.firstName.ilike(f"%{filters['firstName']}%"))

    if filters.get("lastName"):
        query = query.filter(User.lastName.ilike(f"%{filters['lastName']}%"))

    if filters.get("email"):
        query = query.filter(User.email.ilike(f"%{filters['email']}%"))

    if filters.get("phone"):
        query = query.filter(User.phone.ilike(f"%{filters['phone']}%"))

    if filters.get("role"):
        query = query.filter(User.role == filters["role"])

    if filters.get("accountStatus"):
        query = query.filter(User.accountStatus == filters["accountStatus"])
    users=query.offset(skip).limit(limit).all()

    if not users:
        return []
    return  [UserResponse.model_validate(u) for u in users]