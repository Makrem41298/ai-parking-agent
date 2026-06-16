from typing import List, Optional
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session, joinedload
from models.payment import PaymentTransaction
from models.reservation import Reservation
from models.subscription import Subscription
from schemas.payment_schema import PaymentTransactionResponse


def filter_payment_transactions(
    db: Session,
    filters: dict,
    skip: int = 0,
    limit: int = 10
) -> List[PaymentTransactionResponse]:
    query = db.query(PaymentTransaction).options(joinedload(PaymentTransaction.event_logs))

    # User scoping filter (secures CLIENT view of their own transactions)
    if filters.get("userId") is not None:
        user_id = filters["userId"]
        res_ids = [r[0] for r in db.query(Reservation.id).filter(Reservation.userId == user_id).all()]
        sub_ids = [s[0] for s in db.query(Subscription.id).filter(Subscription.userId == user_id).all()]
        query = query.filter(
            or_(
                and_(PaymentTransaction.paymentableType == "reservation", PaymentTransaction.paymentableId.in_(res_ids or [-1])),
                and_(PaymentTransaction.paymentableType == "subscription", PaymentTransaction.paymentableId.in_(sub_ids or [-1]))
            )
        )

    # Exact filters
    if filters.get("id") is not None:
        query = query.filter(PaymentTransaction.id == filters["id"])

    if filters.get("paymentableId") is not None:
        query = query.filter(PaymentTransaction.paymentableId == filters["paymentableId"])

    if filters.get("paymentableType") is not None:
        query = query.filter(PaymentTransaction.paymentableType == filters["paymentableType"])

    if filters.get("status") is not None:
        query = query.filter(PaymentTransaction.status == filters["status"])

    if filters.get("stripeSessionId") is not None:
        query = query.filter(PaymentTransaction.stripeSessionId == filters["stripeSessionId"])

    # Order by paymentDateTime descending to get newest first
    query = query.order_by(PaymentTransaction.paymentDateTime.desc())

    transactions = query.offset(skip).limit(limit).all()

    if not transactions:
        return []

    return [
        PaymentTransactionResponse.model_validate(t)
        for t in transactions
    ]
