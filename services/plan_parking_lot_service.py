from sqlalchemy.orm import Session, joinedload

from models.plan_parking_lot import PlanParkingLot


def get_all_plan_parking_lots(db: Session):
    return (
        db.query(PlanParkingLot)
        .options(
            joinedload(PlanParkingLot.plan),
            joinedload(PlanParkingLot.parking_lot)
        )
        .all()
    )


def get_plan_parking_lot(plan_parking_lot_id: int, db: Session):
    return (
        db.query(PlanParkingLot)
        .options(
            joinedload(PlanParkingLot.plan),
            joinedload(PlanParkingLot.parking_lot)
        )
        .filter(PlanParkingLot.id == plan_parking_lot_id)
        .first()
    )