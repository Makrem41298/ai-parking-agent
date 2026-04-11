from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from database.db import Base
from schemas.reclamation_schema import ReclamationStatus


class Reclamation(Base):
    __tablename__ = "reclamations"

    id = Column(Integer, primary_key=True, index=True)
    clientId = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    adminId = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    subject = Column(String, nullable=True)
    content = Column(String, nullable=False)
    solution = Column(String, nullable=True)
    status = Column(Enum(ReclamationStatus), nullable=False, default=ReclamationStatus.IN_PROGRESS)

    client = relationship("User", foreign_keys=[clientId], back_populates="client_reclamations")
    admin = relationship("User", foreign_keys=[adminId], back_populates="admin_reclamations")