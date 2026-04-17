from sqlalchemy.orm import Session, joinedload

from models.parkingLot import ParkingLot


from sqlalchemy.orm import Session


from sqlalchemy.orm import Session, joinedload

from models.parkingLot import ParkingLot
from schemas.parking_lot_schema import ParkingLotResponse


def get_parking_lots(
    db: Session,
    filters: dict,
    skip: int = 0,
    limit: int = 20
) -> list[ParkingLotResponse]:
    query = (
        db.query(ParkingLot)

    )

    if filters.get("id") is not None:
        query = query.filter(ParkingLot.id == filters["id"])

    if filters.get("name"):
        query = query.filter(ParkingLot.name.ilike(f"%{filters['name']}%"))

    if filters.get("address"):
        query = query.filter(ParkingLot.address.ilike(f"%{filters['address']}%"))

    if filters.get("city"):
        query = query.filter(ParkingLot.city.ilike(f"%{filters['city']}%"))

    if filters.get("country"):
        query = query.filter(ParkingLot.country.ilike(f"%{filters['country']}%"))

    if filters.get("covered") is not None:
        query = query.filter(ParkingLot.covered == filters["covered"])

    if filters.get("numberOfPlaces") is not None:
        query = query.filter(ParkingLot.numberOfPlaces == filters["numberOfPlaces"])

    if filters.get("numberOfPlaceAvailable") is not None:
        query = query.filter(
            ParkingLot.numberOfPlaceAvailable == filters["numberOfPlaceAvailable"]
        )

    if filters.get("description"):
        query = query.filter(ParkingLot.description.ilike(f"%{filters['description']}%"))

    if filters.get("statusParking") is not None:
        query = query.filter(ParkingLot.statusParking == filters["statusParking"])

    if filters.get("reservationAvailability") is not None:
        query = query.filter(
            ParkingLot.reservationAvailability == filters["reservationAvailability"]
        )

    if filters.get("subscriptionAvailability") is not None:
        query = query.filter(
            ParkingLot.subscriptionAvailability == filters["subscriptionAvailability"]
        )

    if filters.get("tarifGridId") is not None:
        query = query.filter(ParkingLot.tarifGridId == filters["tarifGridId"])

    parking_lots = query.offset(skip).limit(limit).all()

    return [ParkingLotResponse.model_validate(p) for p in parking_lots]

def get_parking_lot(parking_id: int, db: Session ):
    return db.query(ParkingLot).options(joinedload(ParkingLot.tarif_grid)).filter(ParkingLot.id == parking_id).first()
