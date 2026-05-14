from sqlalchemy.orm import Session
from models.tarifGrid import TarifGrid
from schemas.tarif_grid_schemas import TarifGridResponse


from sqlalchemy.orm import Session
from models.tarifGrid import TarifGrid
from schemas.tarif_grid_schemas import TarifGridResponse


def filter_tarif_grids(
    db: Session,
    filters: dict,
    skip: int = 0,
    limit: int = 20
):

    query = db.query(TarifGrid)

    if filters.get("id") is not None:
        query = query.filter(TarifGrid.id == filters["id"])

    if filters.get("name"):
        query = query.filter(TarifGrid.name.ilike(f"%{filters['name']}%"))

    results = query.offset(skip).limit(limit).all()

    return [TarifGridResponse.model_validate(t) for t in results]