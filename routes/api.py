from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database.db import get_db
from schemas import user_schemas, tarif_grid_schemas, parking_lot_schema
from schemas.plan_parking_lot_schema import PlanParkingLotResponse
from schemas.plan_schema import PlanResponse
from schemas.reclamation_schema import ReclamationResponse
from schemas.reservation_schema import ReservationResponse
from schemas.subscription_schema import SubscriptionResponse
from schemas.user_schemas import UserResponse
from services import user_service, tarif_grid_service, parking_lot_service
from typing import List

from services.plan_parking_lot_service import get_all_plan_parking_lots, get_plan_parking_lot
from services.plan_service import get_all_plans, get_plan
from services.reclamation_service import get_all_reclamations, get_reclamation
from services.reservation_service import get_reservation as get_reservation_service

from services.reservation_service import get_all_reservation, get_reservation
from services.subscription_service import get_all_subscriptions, get_subscription

api_router = APIRouter()

@api_router.get("/")
async def welcome():
    return {"message": "Hello World"}



@api_router.get("/users", response_model=list[user_schemas.UserResponse])
def read_users(db: Session = Depends(get_db)):
    return user_service.get_users(db)


@api_router.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    userdb = user_service.get_user(db, user_id)
    if not userdb:
        raise HTTPException(status_code=404, detail="User not found")
    return userdb
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





@api_router.get("/plans", response_model=list[PlanResponse])
def read_all_plans(db: Session = Depends(get_db)):
    return get_all_plans(db)


@api_router.get("/plans/{plan_id}", response_model=PlanResponse)
def read_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = get_plan(plan_id, db)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan
@api_router.get("/plan-parking-lot", response_model=list[PlanParkingLotResponse])
def read_all_plan_parking_lots(db: Session = Depends(get_db)):
    return get_all_plan_parking_lots(db)


@api_router.get("/plan-parking-lot/{plan_parking_lot_id}", response_model=PlanParkingLotResponse)
def read_plan_parking_lot(plan_parking_lot_id: int, db: Session = Depends(get_db)):
    item = get_plan_parking_lot(plan_parking_lot_id, db)
    if not item:
        raise HTTPException(status_code=404, detail="PlanParkingLot not found")
    return item



@api_router.get("/subscriptions", response_model=list[SubscriptionResponse])
def read_all_subscriptions(db: Session = Depends(get_db)):
    return get_all_subscriptions(db)


@api_router.get("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
def read_subscription(subscription_id: int, db: Session = Depends(get_db)):
    subscription = get_subscription(subscription_id, db)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription





@api_router.get("/reclamations", response_model=list[ReclamationResponse])
def read_all_reclamations(db: Session = Depends(get_db)):
    return get_all_reclamations(db)


@api_router.get("/reclamation/{reclamation_id}", response_model=ReclamationResponse)
def read_reclamation(reclamation_id: int, db: Session = Depends(get_db)):
    reclamation = get_reclamation(reclamation_id, db)
    if not reclamation:
        raise HTTPException(status_code=404, detail="Reclamation not found")
    return reclamation