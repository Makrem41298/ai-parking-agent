from sqlalchemy.orm import Session
from models.tarifGrid import TariflGrid


def get_tarif_grids(db: Session):
    return db.query(TariflGrid).all()


def get_tarif_grid(db: Session, tarif_grid_id: int):
    return db.query(TariflGrid).filter(TariflGrid.id == tarif_grid_id).first()
