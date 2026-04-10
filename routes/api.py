from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from schemas import user_schemas, tarif_grid_schemas
from services import user_service, tarif_grid_service
from typing import List
api_router = APIRouter()

@api_router.get("/")
async def welcome():
    return {"message": "Hello World"}



@api_router.get("/users", response_model=list[user_schemas.UserResponse])
def read_users(db: Session = Depends(get_db)):
    return user_service.get_users(db)


@api_router.get("/users/{user_id}", response_model=user_schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    userdb = user_service.get_user(db, user_id)
    if not userdb:
        raise HTTPException(status_code=404, detail="User not found")
    return user_service
@api_router.get(  "/tarif-grid",response_model=List[tarif_grid_schemas.TarifGridResponse],  summary="Get all tariff grids")
def get_all_tariff_grids(db: Session = Depends(get_db)):
    grids = tarif_grid_service.get_tarif_grids(db)
    return grids


@api_router.get("/tarif-grid/{tarif_grid_id}",response_model=tarif_grid_schemas.TarifGridResponse,  summary="Get a single tariff grid by ID")
def get_tariff_grid(tarif_grid_id: int,db: Session = Depends(get_db)):
    grid = tarif_grid_service.get_tarif_grid(db, tarif_grid_id)
    if not grid:
        raise HTTPException(status_code=404, detail="Tariff grid not found")
    return grid