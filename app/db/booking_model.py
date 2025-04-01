from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.db import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    spot_id = Column(Integer, nullable=False)
    total_slots = Column(Integer, nullable=False)
    start_date_time = Column(String, nullable=False)
    end_date_time = Column(String, nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    status = Column(String,nullable=False, insert_default="Pending")
    created_at = Column(DateTime, server_default=func.now())
