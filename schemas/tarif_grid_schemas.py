from pydantic import BaseModel, ConfigDict


class TarifGridItem(BaseModel):
    minutes: int
    price: float


class TarifGridResponse(BaseModel):
    name: str
    grid: list[TarifGridItem]

    model_config = ConfigDict(from_attributes=True)