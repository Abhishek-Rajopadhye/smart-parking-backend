import pytest
from sqlalchemy.orm import Session
from app.db.review_model import Review
from app.schemas.review import ReviewCreate, ReviewUpdate
from tests.test_config import client, db, clean_test_db
from app.db.oauth_model import OAuthUser
from app.db.spot_model import Spot
from datetime import datetime


@pytest.fixture
def create_test_review(db: Session):
    """Fixture to create a test review in the database."""
    # Create a mock user
    user = OAuthUser(
        provider="google",
        provider_id="test_user",
        email="test@example.com",
        name="Test User",
        profile_picture="http://example.com/avatar.png",
        access_token="mock_token"
    )
    db.add(user)

    # Create a mock spot
    spot = Spot(
        spot_id=1,
        owner_id="test_user",
        spot_title="Test Spot",
        address="123 Test St",
        latitude=0.0,
        longitude=0.0,
        hourly_rate=10.0,
        no_of_slots=5,
        available_slots=5,
        open_time="08:00:00",
        close_time="20:00:00",
        description="Test spot description",
        available_days=["Monday", "Tuesday"],
        created_at=datetime.now()
    )
    db.add(spot)

    # Commit user and spot before creating the review
    db.commit()

    # Create a mock review
    review = Review(
        user_id="test_user",
        spot_id=1,
        rating_score=5,
        review_description="Great spot!",
        images=[],
        owner_reply=None
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def test_create_review(db: Session):
    """
    Test creating a new review.
    """
    # Setup: create user and spot
    user = OAuthUser(
        provider="google",
        provider_id="test_user",
        email="test@example.com",
        name="Test User",
        profile_picture="http://example.com/avatar.png",
        access_token="mock_token"
    )
    db.add(user)
    spot = Spot(
        spot_id=1,
        owner_id="test_user",
        spot_title="Test Spot",
        address="123 Test St",
        latitude=0.0,
        longitude=0.0,
        hourly_rate=10.0,
        no_of_slots=5,
        available_slots=5,
        open_time="08:00:00",
        close_time="20:00:00",
        description="Test spot description",
        available_days=["Monday", "Tuesday"],
        created_at=datetime.now()
    )
    db.add(spot)
    db.commit()

    # Test data
    test_review_data = {
        "user_id": "test_user",
        "spot_id": 1,
        "rating_score": 5,
        "review_description": "Great spot!",
        "images": [],
        "owner_reply": None,
    }
    response = client.post("/reviews/", json=test_review_data)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == test_review_data["user_id"]
    assert data["spot_id"] == test_review_data["spot_id"]
    assert data["rating_score"] == test_review_data["rating_score"]
    assert data["review_description"] == test_review_data["review_description"]


def test_get_review(create_test_review):
    """
    Test retrieving a review by its ID.
    """
    review = create_test_review
    response = client.get(f"/reviews/{review.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == review.id
    assert data["user_id"] == review.user_id
    assert data["spot_id"] == review.spot_id


def test_get_reviews_by_spot(create_test_review):
    """
    Test retrieving all reviews for a specific spot.
    """
    review = create_test_review
    response = client.get(f"/reviews/spot/{review.spot_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["spot_id"] == review.spot_id


def test_update_review(create_test_review):
    """
    Test updating an existing review.
    """
    review = create_test_review
    updated_data = {
        "user_id": review.user_id,
        "spot_id": review.spot_id,
        "rating_score": 4,
        "review_description": "Updated review description",
        "images": [],
        "owner_reply": "Thank you for your feedback!",
    }
    response = client.put(f"/reviews/{review.id}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["rating_score"] == updated_data["rating_score"]
    assert data["review_description"] == updated_data["review_description"]
    assert data["owner_reply"] == updated_data["owner_reply"]


def test_delete_review(create_test_review):
    """
    Test deleting a review by its ID.
    """
    review = create_test_review
    response = client.delete(f"/reviews/{review.id}")
    assert response.status_code == 200
    assert response.json() is True

    # Verify the review is deleted
    response = client.get(f"/reviews/{review.id}")
    assert response.status_code == 404


def test_get_nonexistent_review():
    """
    Test retrieving a review that does not exist.
    """
    response = client.get(
        "/reviews/9999")  # Assuming 9999 is a non-existent ID
    assert response.status_code == 404
    assert response.json()["detail"] == "Review not found"


def test_delete_nonexistent_review():
    """
    Test deleting a review that does not exist.
    """
    response = client.delete(
        "/reviews/9999")  # Assuming 9999 is a non-existent ID
    assert response.status_code == 404
    assert response.json()["detail"] == "Review not found"
