from sqlalchemy.orm import Session, joinedload

from models.subscription import Subscription


def get_all_subscriptions(db: Session):
    return (
        db.query(Subscription)
        .options(
            joinedload(Subscription.plan_parking_lot),
            joinedload(Subscription.user)
        )
        .all()
    )


def get_subscription(subscription_id: int, db: Session):
    return (
        db.query(Subscription)
        .options(
            joinedload(Subscription.plan_parking_lot),
            joinedload(Subscription.user)
        )
        .filter(Subscription.id == subscription_id)
        .first()
    )

