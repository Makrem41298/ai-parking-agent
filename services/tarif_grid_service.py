from sqlalchemy.orm import Session
from models.tarifGrid import TarifGrid


def get_tarif_grids(db: Session):
    return db.query(TarifGrid).all()


def get_tarif_grid(db: Session, tarif_grid_id: int):
    return db.query(TarifGrid).filter(TarifGrid.id == tarif_grid_id).first()
