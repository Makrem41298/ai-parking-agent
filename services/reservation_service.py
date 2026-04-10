from sqlalchemy.orm import Session, joinedload

from models.reservation import Reservation


def get_all_reservation(db: Session):
    reservations = (
        db.query(Reservation)
        .options(
            joinedload(Reservation.parking_lot),
            joinedload(Reservation.user)
        )
        .all()
    )
    return reservations


def get_reservation(reservation_id: int, db: Session):
    reservation = (
        db.query(Reservation)
        .options(
            joinedload(Reservation.parking_lot),
            joinedload(Reservation.user)
        )
        .filter(Reservation.id == reservation_id)
        .first()
    )
    return  reservation