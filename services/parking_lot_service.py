from sqlalchemy.orm import Session, joinedload

from models.parkingLot import ParkingLot


def get_all_parking_lots(db: Session):
    return db.query(ParkingLot).options(joinedload(ParkingLot.tarif_grid)).all()
def get_parking_lot(parking_id: int, db: Session ):
    return db.query(ParkingLot).options(joinedload(ParkingLot.tarif_grid)).filter(ParkingLot.id == parking_id).first()
