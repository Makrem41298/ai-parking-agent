from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from schemas import schemas
from services import user

api_router = APIRouter()

@api_router.get("/")
async def welcome():
    return {"message": "Hello World"}



@api_router.get("/users", response_model=list[schemas.UserResponse])
def read_users(db: Session = Depends(get_db)):
    return user.get_users(db)


@api_router.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    userdb = user.get_user(db, user_id)
    if not userdb:
        raise HTTPException(status_code=404, detail="User not found")
    return user

