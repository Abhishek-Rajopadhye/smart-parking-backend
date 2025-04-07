# app/db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.booking_model import Booking
from app.db.oauth_model import OAuthUser
from app.db.payment_model import Payment
from app.db.review_model import Review
from app.db.spot_model import Spot
from app.db.db import Base

# SQLAlchemy database URL
DATABASE_URL = settings.DATABASE_URL

# Create database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

# Create a session factory
SessionLocal = sessionmaker(autoflush=False, bind=engine)

# Create all tables
# Base.metadata.create_all(bind=engine)

# Dependency to get a session instance
def get_db():
    """Yield a new database session for dependency injection in FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
