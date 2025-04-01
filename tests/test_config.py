import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.services.auth_service import verify_oauth_token
from app.db.session import get_db, Base
from app.db.oauth_model import OAuthUser
from app.db.payment_model import Payment
from app.db.booking_model import Booking
from app.db.spot_model import Spot
from app.db.review_model import Review
import os
from dotenv import load_dotenv

load_dotenv()
DB_USER: str = os.getenv("DB_USER")
DB_PASSWORD: str = str(os.getenv("DB_PASSWORD", ""))
DB_HOST: str = os.getenv("DB_HOST", "localhost")
DB_PORT: str = os.getenv("DB_PORT", "5432")

# Create a test database engine
TEST_DATABASE_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/test"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the test database tables
Base.metadata.create_all(bind=engine)

# Dependency override for testing
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def mock_verify_oauth_token(token: str, provider: str):
    """
    Mock function to simulate OAuth token verification.
    """
    if token == "mock_token":
        return 
    raise HTTPException(status_code=401, detail="Invalid token")

# Override the dependency
app.dependency_overrides[verify_oauth_token] = mock_verify_oauth_token

client = TestClient(app)

# Define the db fixture
@pytest.fixture(scope="function")
def db():
    """Provide a database session for tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

