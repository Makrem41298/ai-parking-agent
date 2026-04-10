from pydantic import BaseModel


class TarifGridItem(BaseModel):
    minutes: int
    price: float


class TarifGridResponse(BaseModel):
    name: str
    grid: list[TarifGridItem]

    class Config:
        orm_mode = True