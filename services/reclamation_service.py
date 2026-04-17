from typing import List

from pydantic import TypeAdapter
from sqlalchemy.orm import Session, joinedload

from models.reclamation import Reclamation
from database import db
from models.user import User
from schemas.reclamation_schema import ReclamationResponse


def filter_reclamations(
    db: Session,
    filters: dict,
    skip: int = 0,
    limit: int = 20
):
    query = db.query(Reclamation)


    # Exact filters
    if filters.get("id") is not None:
        query = query.filter(Reclamation.id == filters["id"])

    if filters.get("clientId") is not None:
        query = query.filter(Reclamation.clientId == filters["clientId"])

    if filters.get("adminId") is not None:
        query = query.filter(Reclamation.adminId == filters["adminId"])

    if filters.get("status") is not None:
        query = query.filter(Reclamation.status == filters["status"])

    # 🔥 Text search
    if filters.get("subject"):
        query = query.filter(Reclamation.subject.ilike(f"%{filters['subject']}%"))

    if filters.get("content"):
        query = query.filter(Reclamation.content.ilike(f"%{filters['content']}%"))

    if filters.get("solution"):
        query = query.filter(Reclamation.solution.ilike(f"%{filters['solution']}%"))

    reclamations=(query.offset(skip).limit(limit).all())

    if not reclamations:
        return []


    return [
        ReclamationResponse.model_validate(r)
        for r in reclamations
    ]




