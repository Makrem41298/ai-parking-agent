
from models.plan_parking_lot import PlanParkingLot, PlanStatus


from sqlalchemy.orm import Session

from schemas.plan_parking_lot_schema import PlanParkingLotResponse, PlanStatus


def filter_plan_parking_lots(
    db: Session,
    filters: dict,
    skip: int = 0,
    limit: int = 20
) -> list[PlanParkingLotResponse]:
    query = (
        db.query(PlanParkingLot)
    )

    if filters.get("id") is not None:
        query = query.filter(PlanParkingLot.id == filters["id"])

    if filters.get("planId") is not None:
        query = query.filter(PlanParkingLot.planId == filters["planId"])

    if filters.get("parkingLotId") is not None:
        query = query.filter(PlanParkingLot.parkingLotId == filters["parkingLotId"])

    if filters.get("status") is not None:
        status = filters["status"]
        if isinstance(status, str):
            status = PlanStatus(status)
        query = query.filter(PlanParkingLot.status == status)

    if filters.get("renewFee") is not None:
        query = query.filter(PlanParkingLot.renewFee == filters["renewFee"])

    if filters.get("subscriptionFee") is not None:
        query = query.filter(PlanParkingLot.subscriptionFee == filters["subscriptionFee"])

    if filters.get("renewFeeMin") is not None:
        query = query.filter(PlanParkingLot.renewFee >= filters["renewFeeMin"])

    if filters.get("renewFeeMax") is not None:
        query = query.filter(PlanParkingLot.renewFee <= filters["renewFeeMax"])

    if filters.get("subscriptionFeeMin") is not None:
        query = query.filter(PlanParkingLot.subscriptionFee >= filters["subscriptionFeeMin"])

    if filters.get("subscriptionFeeMax") is not None:
        query = query.filter(PlanParkingLot.subscriptionFee <= filters["subscriptionFeeMax"])

    results = query.offset(skip).limit(limit).all()

    return [PlanParkingLotResponse.model_validate(p) for p in results]