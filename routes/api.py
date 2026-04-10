from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database.db import get_db
from schemas import user_schemas, tarif_grid_schemas, parking_lot_schema
from schemas.reservation_schema import ReservationResponse
from services import user_service, tarif_grid_service, parking_lot_service
from typing import List
from services.reservation_service import get_reservation as get_reservation_service

from services.reservation_service import get_all_reservation, get_reservation

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
@api_router.get(
    "/parking-lot",
    response_model=list[parking_lot_schema.ParkingLotResponse],
    summary="Get all parking lots"
)
def get_all_parking_lots(db: Session = Depends(get_db)):
    parking_lots = parking_lot_service.get_all_parking_lots(db)
    return parking_lots
# -----------------------------
# GET ONE
# -----------------------------


@api_router.get(
    "/parking-lot/{parking_lot_id}",
    response_model=parking_lot_schema.ParkingLotResponse,
    summary="Get a single parking lot"
)
def get_parking_lot(parking_lot_id: int, db: Session = Depends(get_db)):
    parking_lot = parking_lot_service.get_parking_lot(parking_lot_id, db)

    if not parking_lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking lot not found"
        )

    return parking_lot






@api_router.get("/reservations", response_model=list[ReservationResponse])
def get_all_reservations(db: Session = Depends(get_db)):
    return get_all_reservation(db)

@api_router.get("/reservations/{reservation_id}")
def read_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = get_reservation_service(reservation_id, db)

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    return  reservation