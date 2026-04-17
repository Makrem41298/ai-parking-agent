from sqlalchemy.orm import Session, joinedload

from models.subscription import Subscription





from datetime import datetime
from sqlalchemy.orm import Session, joinedload

from models.subscription import Subscription
from models.user import User
from models.plan_parking_lot import PlanParkingLot
from schemas.subscription_schema import SubscriptionResponse, SubscriptionStatus


def filter_subscriptions(
    db: Session,
    filters: dict,
    skip: int = 0,
    limit: int = 20
) -> list[SubscriptionResponse]:
    query = (
        db.query(Subscription)
        .options(
            joinedload(Subscription.user),
            joinedload(Subscription.plan_parking_lot)
        )
    )

    if filters.get("id") is not None:
        query = query.filter(Subscription.id == filters["id"])

    if filters.get("status") is not None:
        status = filters["status"]
        if isinstance(status, str):
            status = SubscriptionStatus(status)
        query = query.filter(Subscription.status == status)

    if filters.get("planParkingLotId") is not None:
        query = query.filter(
            Subscription.planParkingLotId == filters["planParkingLotId"]
        )

    if filters.get("userId") is not None:
        query = query.filter(Subscription.userId == filters["userId"])

    if filters.get("startDateFrom") is not None:
        query = query.filter(Subscription.startDate >= filters["startDateFrom"])

    if filters.get("startDateTo") is not None:
        query = query.filter(Subscription.startDate <= filters["startDateTo"])

    if filters.get("endDateFrom") is not None:
        query = query.filter(Subscription.endDate >= filters["endDateFrom"])

    if filters.get("endDateTo") is not None:
        query = query.filter(Subscription.endDate <= filters["endDateTo"])

    if filters.get("isActive") is True:
        now = datetime.utcnow()
        query = query.filter(
            Subscription.startDate <= now,
            Subscription.endDate >= now,
            Subscription.status == SubscriptionStatus.ACTIVE
        )

    if filters.get("userEmail"):
        query = query.join(Subscription.user).filter(
            User.email.ilike(f"%{filters['userEmail']}%")
        )

    if filters.get("userName"):
        name = filters["userName"]
        query = query.join(Subscription.user).filter(
            (User.firstName.ilike(f"%{name}%")) |
            (User.lastName.ilike(f"%{name}%"))
        )

    if filters.get("planParkingLotIds"):
        query = query.filter(
            Subscription.planParkingLotId.in_(filters["planParkingLotIds"])
        )

    subscriptions = query.offset(skip).limit(limit).all()

    return [SubscriptionResponse.model_validate(s) for s in subscriptions]

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

