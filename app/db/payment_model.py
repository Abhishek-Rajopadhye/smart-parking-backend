from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.db import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    spot_id = Column(Integer, nullable=False)  # (parking id)
    amount = Column(Integer, nullable=False)
    razorpay_order_id = Column(String, unique=True, nullable=False)
    razorpay_payment_id = Column(String, unique=True, nullable=True)
    razorpay_signature = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, server_default=func.now())
