from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database.__init__ import Base
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
    REFUND_REQUESTED = "REFUND_REQUESTED"


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    paymentDateTime = Column(DateTime, nullable=True)
    method = Column(String(255), nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    paymentableId = Column(Integer, nullable=False)
    paymentableType = Column(String(255), nullable=False)
    createdAt = Column(DateTime, nullable=False)
    updatedAt = Column(DateTime, nullable=False)
    stripeSessionId = Column(String(255), nullable=True)

    event_logs = relationship("EventLog", back_populates="payment_transaction", cascade="all, delete-orphan")


class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(Integer, primary_key=True, index=True)
    paymentTransactionId = Column(Integer, ForeignKey("payment_transactions.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    createdAt = Column(DateTime, nullable=False)

    payment_transaction = relationship("PaymentTransaction", back_populates="event_logs")
