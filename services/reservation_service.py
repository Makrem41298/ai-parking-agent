from sqlalchemy.orm import Session, joinedload

from models.reservation import Reservation
from schemas.reservation_schema import ReservationResponse


def filter_reservations(
    db: Session,
    filters: dict,
    skip: int = 0,
    limit: int = 20
):
    query = db.query(Reservation)

    # Exact filters
    if filters.get("id") is not None:
        query = query.filter(Reservation.id == filters["id"])

    if filters.get("userId") is not None:
        query = query.filter(Reservation.userId == filters["userId"])

    if filters.get("parkingLotId") is not None:
        query = query.filter(Reservation.parkingLotId == filters["parkingLotId"])

    if filters.get("status") is not None:
        query = query.filter(Reservation.status == filters["status"])

    if filters.get("totalPrice") is not None:
        query = query.filter(Reservation.totalPrice == filters["totalPrice"])

    # 🔥 Date range filters
    if filters.get("startDateFrom") is not None:
        query = query.filter(Reservation.startTimeDate >= filters["startDateFrom"])

    if filters.get("startDateTo") is not None:
        query = query.filter(Reservation.startTimeDate <= filters["startDateTo"])

    if filters.get("endDateFrom") is not None:
        query = query.filter(Reservation.endTimeDate >= filters["endDateFrom"])

    if filters.get("endDateTo") is not None:
        query = query.filter(Reservation.endTimeDate <= filters["endDateTo"])

    if filters.get("entryTimeFrom") is not None:
        query = query.filter(Reservation.entryTime >= filters["entryTimeFrom"])

    if filters.get("entryTimeTo") is not None:
        query = query.filter(Reservation.entryTime <= filters["entryTimeTo"])
    reservation=query.offset(skip).limit(limit).all()
    if not reservation:
        return []
    return [
        ReservationResponse.model_validate(r) for r in reservation
    ]


