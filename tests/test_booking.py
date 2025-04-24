import pytest
from sqlalchemy.orm import Session
from datetime import datetime
from tests.test_config import client, db, clean_test_db
from app.db.oauth_model import OAuthUser
from app.db.payment_model import Payment
from app.db.spot_model import Spot

@pytest.fixture
def create_test_data(db: Session):
    # Create test user
    user = OAuthUser(
        provider="google",
        provider_id="test_user",
        email="test@example.com",
        name="Test User",
        profile_picture="http://example.com/avatar.png",
        access_token="mock_token"
    )

    # Create owner
    owner = OAuthUser(
        provider="google",
        provider_id="owner_test",
        email="owner@example.com",
        name="Test Owner",
        profile_picture="http://example.com/avatar.png",
        access_token="mock_token"
    )

    # Create parking spot
    spot = Spot(
        owner_id="owner_test",
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
        image=[b"mock_image_data"],
        created_at=datetime.now()
    )

    db.add_all([user, owner, spot])
    db.commit()

    return spot, user, owner

def test_valid_booking(create_test_data):
    spot, user, owner = create_test_data
    payload = {
        "user_id": user.provider_id,
        "spot_id": spot.spot_id,
        "total_slots": 2,
        "start_date_time": "2023-10-01T10:00:00",
        "end_date_time": "2023-10-01T12:00:00",
        "total_amount": 20,
        "receipt": "mock_receipt"
    }
    response = client.post("/bookings/book-spot/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "order_id" in data
    assert "amount" in data
    assert "currency" in data
    assert "payment_id" in data
    assert "payment_status" in data
    assert "receipt" in data

def test_invalid_booking(create_test_data):
    spot, user, owner = create_test_data
    payload = {
        "user_id": user.provider_id,
        "spot_id": spot.spot_id,
        "total_slots": 10,  # Exceeds available slots
        "start_date_time": "2023-10-01T10:00:00",
        "end_date_time": "2023-10-01T12:00:00",
        "total_amount": 100,
        "receipt": "mock_receipt"
    }
    response = client.post("/bookings/book-spot/", json=payload)
    assert response.status_code == 400
    assert response.json() == {"detail": "Failed to book the spot"}

def test_update_booking_valid(create_test_data, db):
    # Create test user, spot, and payment entry
    spot, user, owner = create_test_data
    payment = Payment(
        id=1,
        user_id=user.provider_id,
        spot_id=spot.spot_id,
        amount=20,
        status="pending",
        razorpay_order_id="order_xyz"
    )
    db.add(payment)
    db.commit()

    payload = {
        "payment_id": 1,
        "razorpay_payment_id": "rp_payment_xyz",
        "razorpay_signature": "valid_signature",
        "start_time": "2025-04-23T10:00:00",
        "end_time": "2025-04-23T12:00:00",
        "total_slots": 1
    }

    response = client.post("/bookings/update-payment-status", json=payload)

    assert response.status_code == 200
    assert response.json()["payment_status"] == "success"

def test_paymenet_not_found(create_test_data, db):
    # Create test user, spot, and payment entry
    spot, user, owner = create_test_data

    payload = {
        "payment_id": 9999,  # Non-existent payment ID
        "razorpay_payment_id": "rp_payment_xyz",
        "razorpay_signature": "valid_signature",
        "start_time": "2025-04-23T10:00:00",
        "end_time": "2025-04-23T12:00:00",
        "total_slots": 1
    }

    response = client.post("/bookings/update-payment-status", json=payload)
    assert response.status_code == 400
    assert response.json() == {"detail": "Failed to update the payment status"}