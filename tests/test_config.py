import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.services.auth_service import verify_oauth_token, verify_google_token, verify_github_token
from app.db.session import get_db, Base
from app.db.oauth_model import OAuthUser
from app.db.payment_model import Payment
from app.db.booking_model import Booking
from app.db.spot_model import Spot, Document
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
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

# Create the test database tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def mock_verify_oauth_token(token: str = None, provider: str = None):
    """
    Mock function to simulate OAuth token verification.
    """
    print(token, provider)
    if(provider=="google"):
        return verify_google_token(token, provider)
    elif(provider=="github"):
        return verify_github_token(token, provider)


def mock_verify_google_token(token: str = None, provider: str = None):
    """
    Mock function to simulate OAuth token verification.
    """
    print(token, provider)
    if(token == "mock_token" and provider=="google"):
        return True

def mock_verify_github_token(token: str = None, provider: str = None):
    """
    Mock function to simulate OAuth token verification.
    """
    print(token, provider)
    if(token == "mock_token" and provider=="github"):
        return True

@pytest.fixture(scope="function", autouse=True)
def clean_test_db():
    """
    Clean up the test database after each test.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield  # Allow the test to run
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="function", name="db")
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Overrides
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[verify_oauth_token] = mock_verify_oauth_token
app.dependency_overrides[verify_google_token] = mock_verify_google_token
app.dependency_overrides[verify_github_token] = mock_verify_github_token


client = TestClient(app)