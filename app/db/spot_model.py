from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, ARRAY, LargeBinary
from sqlalchemy.sql import func
from app.db.db import Base


class Spot(Base):
    __tablename__ = "spots"

    spot_id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(String, ForeignKey(
        "oauth_users.provider_id"), index=True)
    spot_title = Column(String, index=True)
    address = Column(String, index=True)
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    hourly_rate = Column(Integer, index=True)
    no_of_slots = Column(Integer, index=True)
    available_slots = Column(Integer, index=True)
    open_time = Column(String, nullable=False)
    close_time = Column(String, nullable=False)
    description = Column(String, nullable=True)
    available_days = Column(ARRAY(String), nullable=False)
    image = Column(ARRAY(LargeBinary), nullable=True)
    verification_status = Column(Integer)  # 0: pending, 1: approved, -1: rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    spot_id = Column(Integer, ForeignKey("spots.spot_id"), index=True)
    document_type = Column(String, nullable=False)  # Identity_proof, supporting_document, ownership_proof
    content = Column(LargeBinary, nullable=False)   # PDF as BLOB
    filename = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
