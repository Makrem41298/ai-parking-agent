from sqlalchemy.orm import Session

from models import Models


def get_user(db: Session, user_id: int):
    return db.query(Models.User).filter(Models.User.id == user_id).first()

def get_users(db: Session):
    return db.query(Models.User).all()



