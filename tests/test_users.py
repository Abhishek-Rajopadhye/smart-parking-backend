import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.oauth_model import OAuthUser
from app.db.payment_model import Payment
from app.db.booking_model import Booking
from app.db.spot_model import Spot
from tests.test_config import client, db

# Helper function to create a mock OAuth user
def create_mock_oauth_user(db: Session, mockUser: dict):
    """
    Create a mock OAuth user and add it to the database.

    Parameters:
        db (Session): The database session to use for adding the user.
        provider (str): The OAuth provider (e.g., 'google', 'facebook').
        provider_id (str): The unique identifier for the user from the OAuth provider.
        email (str): The email address of the user.

    Returns:
        OAuthUser: The created OAuth user object.

    Raises:
        SQLAlchemyError: If there is an error committing the user to the database.
    """
    user = OAuthUser(
        provider=mockUser["provider"],
        provider_id=mockUser["provider_id"],
        email=mockUser["email"],
        name=mockUser["name"],
        profile_picture=mockUser["profile_picture"],
        access_token=mockUser["access_token"]
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Helper function to create a mock spot
def create_mock_spot(db: Session, mockSpot: dict):
    spot = Spot(
        spot_id=mockSpot["spot_id"],
        owner_id=mockSpot["owner_id"],
        spot_title=mockSpot["spot_title"],
        address=mockSpot["address"],
        latitude=mockSpot["latitude"],
        longitude=mockSpot["longitude"],
        hourly_rate=mockSpot["hourly_rate"],
        no_of_slots=mockSpot["no_of_slots"],
        available_slots=mockSpot["available_slots"],
        open_time=mockSpot["open_time"],
        close_time=mockSpot["close_time"],
        description=mockSpot["description"],
        available_days=mockSpot["available_days"],
        image=mockSpot["image"],
        created_at=mockSpot["created_at"]
    )
    db.add(spot)
    db.commit()
    db.refresh(spot)
    return spot

# Helper function to create a mock booking and payment
def create_mock_booking_and_payment(db: Session, mockBooking: dict, mockPayment: dict):
    payment = Payment(
        id=mockPayment["id"],
        user_id=mockPayment["user_id"],
        spot_id=mockPayment["spot_id"],
        amount=mockPayment["amount"],
        razorpay_order_id=mockPayment["razorpay_order_id"],
        razorpay_payment_id=mockPayment["razorpay_payment_id"],
        razorpay_signature=mockPayment["razorpay_signature"],
        status=mockPayment["status"],
        created_at=mockPayment["created_at"],
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    booking = Booking(
        id=mockBooking["id"],
        user_id=mockBooking["user_id"],
        spot_id=mockBooking["spot_id"],
        total_slots=mockBooking["total_slots"],
        start_date_time=mockBooking["start_date_time"],
        end_date_time=mockBooking["end_date_time"],
        payment_id=mockBooking["payment_id"],
        status=mockBooking["status"],
        created_at=mockBooking["created_at"],
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking, payment


# Test case for fetching user profile
def test_get_user_profile(db: Session):
    # Create mock user, spot, and booking

    mockUser = {
        "provider": "google",
        "provider_id": "1",
        "email": "mock_user@example.com",
        "name": "Test User",
        "profile_picture":"http://example.com/avatar.png",
        "access_token":"mock_token"
    }
    mockSpot = {
        "spot_id": 1,
        "owner_id": "1",
        "spot_title": "Test Spot",
        "address": "Test Address",
        "latitude": 111.0,
        "longitude": 111.0,
        "hourly_rate": 11.0,
        "no_of_slots": 11,
        "available_slots": 1,
        "open_time": "08:00:00",
        "close_time": "20:00:00",
        "description": "This is a test spot for parking.",
        "available_days": ["Monday", "Tuesday", "Wednesday"],
        "image": b"mock_image_data",
        "created_at": datetime.now(),
    }
    mockBooking = {
        "id": 1,
        "user_id": "1",
        "spot_id": 1,
        "total_slots": 2,
        "start_date_time": "2025-03-01T10:00:00",
        "end_date_time": "2025-03-01T12:00:00",
        "payment_id": 1,
        "status": "confirmed",
        "created_at": datetime.now(),
    }
    mockPayment = {
        "id": 1,
        "user_id": "1",
        "spot_id": 1,
        "amount": 100.0,
        "razorpay_order_id": "order_123",
        "razorpay_payment_id": "payment_123",
        "razorpay_signature": "signature_123",
        "status": "success",
        "created_at": datetime.now(),
    }

    user = create_mock_oauth_user(db, mockUser)
    spot = create_mock_spot(db, mockSpot)
    create_mock_booking_and_payment(db, mockBooking=mockBooking, mockPayment=mockPayment)

    # Fetch user profile
    response = client.get(f"/users/profile/{user.provider_id}", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == user.provider_id
    assert data["name"] == user.name
    assert data["email"] == user.email
    assert data["total_earnings"] == 100
    assert data["profile_picture"] == user.profile_picture

# Test case for updating user profile
def test_update_user_profile(db: Session):
    # Create mock user
    mockUser = {
        "provider": "google",
        "provider_id": "2",
        "email": "mock_user2@example.com",
        "name": "Test User",
        "profile_picture":"http://example.com/avatar.png",
        "access_token":"mock_token"
    }
    user = create_mock_oauth_user(db, mockUser)

    # Update user profile
    update_data = {
        "name": "Updated User",
        "email": "updated2@example.com",
        "phone": "1234567890",
        "profile_picture": "http://example.com/updated_avatar.png",
        "total_earnings": 0  # This field is ignored during updates
    }
    response = client.put(f"/users/profile/{user.provider_id}", json=update_data, headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == user.provider_id
    assert data["name"] == update_data["name"]
    assert data["email"] == update_data["email"]
    assert data["phone"] == update_data["phone"]
    assert data["profile_picture"] == update_data["profile_picture"]

