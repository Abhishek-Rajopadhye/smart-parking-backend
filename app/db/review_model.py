
from sqlalchemy import Column, Integer, String, DateTime, LargeBinary, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.db import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey(
        "oauth_users.provider_id"), nullable=False)
    spot_id = Column(Integer, ForeignKey("spots.spot_id"), nullable=False)
    rating_score = Column(Integer, nullable=False)
    review_description = Column(String, nullable=True)
    images = Column(ARRAY(LargeBinary), nullable=True)
    owner_reply = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("OAuthUser", backref="reviews")
