from sqlalchemy.orm import Session

from models.plan import Plan


def get_all_plans(db: Session):
    return db.query(Plan).all()


def get_plan(plan_id: int, db: Session):
    return db.query(Plan).filter(Plan.id == plan_id).first()