from sqlalchemy import Column, Integer, String, JSON
from database.db import Base

class TariflGrid (Base):
    __tablename__="tariff_grids"
    id= Column(Integer,primary_key=True,index=True)
    name=Column(String(100),nullable=False)
    grid=Column(JSON,nullable=False)


