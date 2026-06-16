import json
from datetime import date, datetime
from typing import Optional, List

from langchain_core.tools import tool

from database import SessionLocal
from services.subscription_service import filter_subscriptions
from services.plan_parking_lot_service import filter_plan_parking_lots
from services.plan_service import filter_plans
from services.user_service import filter_users
from services.reclamation_service import filter_reclamations
from services.tarif_grid_service import filter_tarif_grids
from services.parking_lot_service import get_parking_lots
from services.reservation_service import filter_reservations
from services.payment_service import filter_payment_transactions


def serialize_results(results, fields=None, max_results=5):
    """Serialize results with optional field filtering and result limit.

    Args:
        results: List of Pydantic model instances.
        fields: Optional set of field names to include. If None, all fields are returned.
        max_results: Maximum number of results to include in the output.
    """
    data = []
    for r in results[:max_results]:
        row = r.model_dump(mode="json")
        if fields:
            row = {k: v for k, v in row.items() if k in fields}
        data.append(row)

    output = json.dumps(data, separators=(',', ':'), default=str)

    if len(results) > max_results:
        output += f"\n[Showing {max_results} of {len(results)} total results]"

    return output


@tool
def get_parking_lots_tool(
        id: Optional[int] = None,
        name: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        covered: Optional[bool] = None,
        statusParking: Optional[str] = None,
        reservationAvailability: Optional[bool] = None,
        subscriptionAvailability: Optional[bool] = None,
        skip: int = 0,
        limit: int = 10,
) -> str:
    """Filter parking lots by id, name, address, city, country, status, or availability."""
    db = SessionLocal()
    try:
        filters = {
            "id": id,
            "name": name,
            "address": address,
            "city": city,
            "country": country,
            "covered": covered,
            "statusParking": statusParking,
            "reservationAvailability": reservationAvailability,
            "subscriptionAvailability": subscriptionAvailability,
        }

        results = get_parking_lots(db, filters, skip, limit)

        return serialize_results(
            results,
            fields={"id", "name", "address", "city", "country", "covered",
                     "statusParking", "numberOfPlaces", "numberOfPlaceAvailable",
                     "reservationAvailability", "subscriptionAvailability"}
        )
    finally:
        db.close()

@tool
def filter_tarif_grids_tool(
        id: Optional[int] = None,
        name: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
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


@tool
def filter_reservations_tool(
        id: Optional[int] = None,
        userId: Optional[int] = None,
        parkingLotId: Optional[int] = None,
        status: Optional[str] = None,
        startDateFrom: Optional[date] = None,
        startDateTo: Optional[date] = None,
        endDateFrom: Optional[date] = None,
        endDateTo: Optional[date] = None,
        skip: int = 0,
        limit: int = 10,
) -> str:
    """Filter reservations by id, user, parking lot, status, or date range."""

    db = SessionLocal()
    try:
        filters = {
            "id": id,
            "userId": userId,
            "parkingLotId": parkingLotId,
            "status": status,
            "startDateFrom": startDateFrom,
            "startDateTo": startDateTo,
            "endDateFrom": endDateFrom,
            "endDateTo": endDateTo,
        }

        results = filter_reservations(
            db=db,
            filters=filters,
            skip=skip,
            limit=limit,
        )

        return serialize_results(
            results,
            fields={"id", "userId", "parkingLotId", "status",
                     "totalPrice", "startTimeDate", "endTimeDate"}
        )
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
        limit: int = 10
) -> str:
    """Filter users by id, name, email, phone, role, or account status."""
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
        skip: int = 0,
        limit: int = 10
) -> str:
    """Filter reclamations by id, client, admin, status, or subject."""

    db = SessionLocal()
    try:
        filters = {
            "id": id,
            "clientId": clientId,
            "adminId": adminId,
            "status": status,
            "subject": subject,
        }

        results = filter_reclamations(db, filters, skip, limit)
        return serialize_results(
            results,
            fields={"id", "clientId", "adminId", "status", "subject", "content", "solution"}
        )

    finally:
        db.close()

@tool
def filter_plans_tool(
        id: Optional[int] = None,
        name: Optional[str] = None,
        NumberOfBenefitDays: Optional[int] = None,
        isActive: Optional[bool] = None,
        skip: int = 0,
        limit: int = 10
) -> str:
    """Filter plans by id, name, benefit days, or active status."""

    db = SessionLocal()
    try:
        filters = {
            "id": id,
            "name": name,
            "NumberOfBenefitDays": NumberOfBenefitDays,
            "isActive": isActive
        }

        results = filter_plans(db, filters, skip, limit)

        return serialize_results(
            results,
            fields={"id", "name", "NumberOfBenefitDays", "startDate", "endDate", "isActive"}
        )
    finally:
        db.close()


@tool
def filter_plan_parking_lots_tool(
        id: Optional[int] = None,
        planId: Optional[int] = None,
        parkingLotId: Optional[List[int]] = None,
        status: Optional[str] = None,
        subscriptionFee: Optional[float] = None,
        renewFee: Optional[float] = None,
        skip: int = 0,
        limit: int = 10
) -> str:
    """Filter plan parking lots by plan, parking lot, status, or fees.

    parkingLotId supports multiple IDs: example -> [3, 4, 5, 7]
    """

    db = SessionLocal()
    try:
        filters = {
            "id": id,
            "planId": planId,
            "parkingLotId": parkingLotId,
            "status": status,
            "renewFee": renewFee,
            "subscriptionFee": subscriptionFee,
        }

        results = filter_plan_parking_lots(
            db,
            filters,
            skip,
            limit
        )

        return serialize_results(
            results,
            fields={"id", "planId", "parkingLotId", "status",
                     "subscriptionFee", "renewFee"}
        )

    finally:
        db.close()

@tool
def filter_subscriptions_tool(
        id: Optional[int] = None,
        status: Optional[str] = None,
        planParkingLotId: Optional[int] = None,
        userId: Optional[int] = None,
        isActive: Optional[bool] = None,
        skip: int = 0,
        limit: int = 10
) -> str:
    """Filter subscriptions by id, status, user, plan parking lot, or active state."""

    db = SessionLocal()
    try:
        filters = {
            "id": id,
            "status": status,
            "planParkingLotId": planParkingLotId,
            "userId": userId,
            "isActive": isActive,
        }

        results = filter_subscriptions(db, filters, skip, limit)

        return serialize_results(
            results,
            fields={"id", "status", "planParkingLotId", "userId",
                     "startDate", "endDate", "isActive"}
        )
    finally:
        db.close()


@tool
def filter_payment_transactions_tool(
        id: Optional[int] = None,
        userId: Optional[int] = None,
        paymentableId: Optional[int] = None,
        paymentableType: Optional[str] = None,
        status: Optional[str] = None,
        stripeSessionId: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
) -> str:
    """Filter payment transactions by id, userId, paymentableId, paymentableType (reservation or subscription), status, or stripeSessionId. Includes associated event logs."""
    db = SessionLocal()
    try:
        filters = {
            "id": id,
            "userId": userId,
            "paymentableId": paymentableId,
            "paymentableType": paymentableType,
            "status": status,
            "stripeSessionId": stripeSessionId,
        }
        results = filter_payment_transactions(db, filters, skip, limit)

        return serialize_results(
            results,
            fields={"id", "amount", "paymentDateTime", "method", "status",
                     "paymentableId", "paymentableType", "createdAt", "updatedAt",
                     "stripeSessionId", "event_logs"}
        )
    finally:
        db.close()


@tool
def unsupported_request(reason: str) -> str:
    """Use this tool when the user asks for something outside available tools."""
    return "This request is not supported by the available tools."
