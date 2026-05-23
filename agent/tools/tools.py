from services.subscription_service import filter_subscriptions
from services.plan_parking_lot_service import filter_plan_parking_lots
from services.plan_service import filter_plans
from services.user_service import filter_users
from services.reclamation_service import filter_reclamations
from datetime import date, datetime
from services.tarif_grid_service import filter_tarif_grids
import json
from typing import Optional
from langchain_core.tools import tool
from services.parking_lot_service import get_parking_lots
def serialize_results(results):
    return json.dumps(
        [r.model_dump(mode="json") for r in results],
        indent=2,
        default=str
    )

@tool
def get_parking_lots_tool(
        id: Optional[int] = None,
        name: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        covered: Optional[bool] = None,
        numberOfPlaces: Optional[int] = None,
        numberOfPlaceAvailable: Optional[int] = None,
        description: Optional[str] = None,
        statusParking: Optional[str] = None,
        reservationAvailability: Optional[bool] = None,
        subscriptionAvailability: Optional[bool] = None,
        tarifGridId: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
) -> str:
    """Filter parking lots by id, name, address, city, country, status, availability, and tariff grid."""

    db = SessionLocal()
    try:
        filters = {
            "id": id,
            "name": name,
            "address": address,
            "city": city,
            "country": country,
            "covered": covered,
            "numberOfPlaces": numberOfPlaces,
            "numberOfPlaceAvailable": numberOfPlaceAvailable,
            "description": description,
            "statusParking": statusParking,
            "reservationAvailability": reservationAvailability,
            "subscriptionAvailability": subscriptionAvailability,
            "tarifGridId": tarifGridId,
        }

        results = get_parking_lots(db, filters, skip, limit)

        return serialize_results(results)
    finally:
        db.close()

@tool
def filter_tarif_grids_tool(
        id: Optional[int] = None,
        name: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
) -> str:
    """Filter tarif grids by id or name."""

    db = SessionLocal()
    try:
        filters = {
            "id": id,
            "name": name
        }

        results = filter_tarif_grids(db, filters, skip, limit)

        return serialize_results(results)
    finally:
        db.close()

from langchain_core.tools import tool
from database import SessionLocal
from services.reservation_service import filter_reservations

@tool
def filter_reservations_tool(
        id: Optional[int] = None,
        userId: Optional[int] = None,
        parkingLotId: Optional[int] = None,
        status: Optional[str] = None,
        totalPrice: Optional[float] = None,
        startDateFrom: Optional[date] = None,
        startDateTo: Optional[date] = None,
        endDateFrom: Optional[date] = None,
        endDateTo: Optional[date] = None,
        entryTimeFrom: Optional[date] = None,
        entryTimeTo: Optional[date] = None,
        skip: int = 0,
        limit: int = 20,
) -> str:
    """Filter reservations by id, user, parking lot, status, price, and date ranges."""

    db = SessionLocal()
    try:
        filters = {
            "id": id,
            "userId": userId,
            "parkingLotId": parkingLotId,
            "status": status,
            "totalPrice": totalPrice,
            "startDateFrom": startDateFrom,
            "startDateTo": startDateTo,
            "endDateFrom": endDateFrom,
            "endDateTo": endDateTo,
            "entryTimeFrom": entryTimeFrom,
            "entryTimeTo": entryTimeTo,
        }

        results = filter_reservations(
            db=db,
            filters=filters,
            skip=skip,
            limit=limit,
        )
        print(results)

        return serialize_results(results)
    finally:
        db.close()

@tool
def filter_users_tool(
        id: int | None = None,
        firstName: str | None = None,
        lastName: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        role: str | None = None,
        accountStatus: str | None = None,
        skip: int = 0,
        limit: int = 20
) -> str:
    """
       Filter users by id, name, email, phone, role, or account status.

       Use this tool when:
       - user asks about users
       - search users by name or email
       - filter by role or status
       """
    db = SessionLocal()

    try:
        filters = {
            "id": id,
            "firstName": firstName,
            "lastName": lastName,
            "email": email,
            "phone": phone,
            "role": role,
            "accountStatus": accountStatus,
        }

        result = filter_users(db, filters, skip, limit)
        return serialize_results(result)

    finally:
        db.close()

@tool
def filter_reclamations_tool(
        id: int | None = None,
        clientId: int | None = None,
        adminId: int | None = None,
        status: str | None = None,
        subject: str | None = None,
        content: str | None = None,
        solution: str | None = None,
        skip: int = 0,
        limit: int = 20
) -> str:
    """Filter reclamations by id, client, admin, status, subject, content, or solution."""

    db = SessionLocal()
    try:
        filters = {
            "id": id,
            "clientId": clientId,
            "adminId": adminId,
            "status": status,
            "subject": subject,
            "content": content,
            "solution": solution,
        }

        results = filter_reclamations(db, filters, skip, limit)
        return serialize_results(results)

    finally:
        db.close()

@tool
def filter_plans_tool(
        id: Optional[int] = None,
        name: Optional[str] = None,
        NumberOfBenefitDays: Optional[int] = None,
        startDateFrom: Optional[datetime] = None,
        startDateTo: Optional[datetime] = None,
        endDateFrom: Optional[datetime] = None,
        endDateTo: Optional[datetime] = None,
        isActive: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
) -> str:
    """Filter plans by name, benefit days, and date ranges."""

    db = SessionLocal()
    try:
        filters = {
            "id": id,
            "name": name,
            "NumberOfBenefitDays": NumberOfBenefitDays,
            "startDateFrom": startDateFrom,
            "startDateTo": startDateTo,
            "endDateFrom": endDateFrom,
            "endDateTo": endDateTo,
            "isActive": isActive
        }

        results = filter_plans(db, filters, skip, limit)

        return json.dumps(
            [r.model_dump(mode="json") for r in results],
            indent=2,
            default=str
        )
    finally:
        db.close()

from typing import Optional, List
from langchain_core.tools import tool

@tool
def filter_plan_parking_lots_tool(
        id: Optional[int] = None,
        planId: Optional[int] = None,

        # CHANGED: int -> List[int]
        parkingLotId: Optional[List[int]] = None,

        status: Optional[str] = None,
        renewFee: Optional[float] = None,
        subscriptionFee: Optional[float] = None,
        renewFeeMin: Optional[float] = None,
        renewFeeMax: Optional[float] = None,
        subscriptionFeeMin: Optional[float] = None,
        subscriptionFeeMax: Optional[float] = None,
        skip: int = 0,
        limit: int = 20
) -> str:
    """
    Filter plan parking lots by plan, parking lot, status,
    renew fee, and subscription fee.

    parkingLotId supports multiple IDs:
    example -> [3, 4, 5, 7]
    """

    db = SessionLocal()
    try:
        filters = {
            "id": id,
            "planId": planId,
            "parkingLotId": parkingLotId,  # now list supported
            "status": status,
            "renewFee": renewFee,
            "subscriptionFee": subscriptionFee,
            "renewFeeMin": renewFeeMin,
            "renewFeeMax": renewFeeMax,
            "subscriptionFeeMin": subscriptionFeeMin,
            "subscriptionFeeMax": subscriptionFeeMax,
        }

        results = filter_plan_parking_lots(
            db,
            filters,
            skip,
            limit
        )

        return serialize_results(results)

    finally:
        db.close()

@tool
def filter_subscriptions_tool(
        id: Optional[int] = None,
        status: Optional[str] = None,
        planParkingLotId: Optional[int] = None,
        userId: Optional[int] = None,
        startDateFrom: Optional[datetime] = None,
        startDateTo: Optional[datetime] = None,
        endDateFrom: Optional[datetime] = None,
        endDateTo: Optional[datetime] = None,
        isActive: Optional[bool] = None,
        userEmail: Optional[str] = None,
        userName: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
) -> str:
    """Filter subscriptions by id, status, user, plan parking lot, dates, and active state."""

    db = SessionLocal()
    try:
        filters = {
            "id": id,
            "status": status,
            "planParkingLotId": planParkingLotId,
            "userId": userId,
            "startDateFrom": startDateFrom,
            "startDateTo": startDateTo,
            "endDateFrom": endDateFrom,
            "endDateTo": endDateTo,
            "isActive": isActive,
            "userEmail": userEmail,
            "userName": userName,
        }

        results = filter_subscriptions(db, filters, skip, limit)

        return serialize_results(results)
    finally:
        db.close()

from langchain.agents import create_agent
from langchain_core.tools import tool

@tool
def unsupported_request(reason: str) -> str:
    """Use this tool when the user asks for something that is خارج available tools."""
    return "This request is not supported by the available tools."
