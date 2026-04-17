from sqlalchemy.orm import Session

from models.plan import Plan


from sqlalchemy.orm import Session
from models.plan import Plan


from sqlalchemy.orm import Session
from models.plan import Plan
from schemas.plan_schema import PlanResponse


def filter_plans(
    db: Session,
    filters: dict,
    skip: int = 0,
    limit: int = 20
) -> list[PlanResponse]:

    query = db.query(Plan)

    # 🔹 Exact filters
    if filters.get("id") is not None:
        query = query.filter(Plan.id == filters["id"])

    if filters.get("name"):
        query = query.filter(Plan.name.ilike(f"%{filters['name']}%"))

    if filters.get("NumberOfBenefitDays") is not None:
        query = query.filter(
            Plan.NumberOfBenefitDays == filters["NumberOfBenefitDays"]
        )

    # 🔥 Date filters
    if filters.get("startDateFrom") is not None:
        query = query.filter(Plan.startDate >= filters["startDateFrom"])

    if filters.get("startDateTo") is not None:
        query = query.filter(Plan.startDate <= filters["startDateTo"])

    if filters.get("endDateFrom") is not None:
        query = query.filter(Plan.endDate >= filters["endDateFrom"])

    if filters.get("endDateTo") is not None:
        query = query.filter(Plan.endDate <= filters["endDateTo"])

    # 🔥 Active plans (today inside range)
    if filters.get("isActive") is True:
        from datetime import datetime
        now = datetime.utcnow()
        query = query.filter(
            Plan.startDate <= now,
            Plan.endDate >= now
        )

    plans = query.offset(skip).limit(limit).all()

    return [PlanResponse.model_validate(p) for p in plans]