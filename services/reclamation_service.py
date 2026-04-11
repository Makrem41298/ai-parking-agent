from sqlalchemy.orm import Session, joinedload

from models.reclamation import Reclamation


def get_all_reclamations(db: Session):
    return (
        db.query(Reclamation)
        .options(
            joinedload(Reclamation.client),
            joinedload(Reclamation.admin)
        )
        .all()
    )


def get_reclamation(reclamation_id: int, db: Session):
    return (
        db.query(Reclamation)
        .options(
            joinedload(Reclamation.client),
            joinedload(Reclamation.admin)
        )
        .filter(Reclamation.id == reclamation_id)
        .first()
    )

