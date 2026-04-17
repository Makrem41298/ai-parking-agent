from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from starlette import status
from datetime import date

from database.__init__ import get_db
from schemas import  tarif_grid_schemas, parking_lot_schema
from schemas.parking_lot_schema import ParkingLotResponse, ParkingStatus
from schemas.plan_parking_lot_schema import PlanParkingLotResponse, PlanStatus
from schemas.reclamation_schema import ReclamationResponse, ReclamationStatus
from schemas.reservation_schema import ReservationResponse, ReservationStatus
from schemas.subscription_schema import SubscriptionResponse, SubscriptionStatus
from schemas.tarif_grid_schemas import TarifGridResponse
from schemas.user_schemas import UserResponse
from services import user_service, tarif_grid_service, parking_lot_service, plan_parking_lot_service
from typing import List, Optional


from services.subscription_service import  get_subscription, filter_subscriptions
from services.tarif_grid_service import filter_tarif_grids
from services.user_service import filter_users

api_router = APIRouter()

@api_router.get("/")
async def welcome():
    return {"message": "Hello World"}
