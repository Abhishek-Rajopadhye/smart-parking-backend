import pytest
from sqlalchemy.orm import Session
from datetime import datetime
from tests.test_config import client, db, clean_test_db
from app.db.oauth_model import OAuthUser
from app.db.payment_model import Payment
from app.db.spot_model import Spot
import base64

@pytest.fixture
def create_test_data(db: Session):
    # Create test user
    user = OAuthUser(
        provider="google",
        provider_id="google-oauth2|1234567890",
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
    db.add_all([user, owner])
    db.commit() 
    return user, owner

def test_valid_spot_as_user(create_test_data):
  data = {
          "owner_id": 'google-oauth2|1234567890',
          "spot_title": "Test Parking Spot",
          "spot_address": "456 Parking St",
          "latitude": "12.34",
          "longitude": "56.78",
          "available_slots": "3",
          "total_slots": "3",
          "hourly_rate": "50",
          "open_time": "09:00:00",
          "close_time": "18:00:00",
          "spot_description": "Spacious and secure.",
          "available_days": "Monday,Tuesday,Friday",
          "verification_status": "3"
      }

      # If image is optional, we pass an empty list or None

  response = client.post("/spots/add-spot", data=data)

  assert response.status_code == 200
  assert response.json()['message'] == "Spot added successfully."

def test_valid_spot_with_image(create_test_data):
    base64_img1 = base64.b64encode(b'0123456789').decode('utf-8')
    base64_img2 = base64.b64encode(b'abcdefghij').decode('utf-8')
    data = {
        "owner_id": "google-oauth2|1234567890",
        "spot_title": "Test Parking Spot",
        "spot_address": "456 Parking St",
        "latitude": "12.34",
        "longitude": "56.78",
        "available_slots": "3",
        "total_slots": "3",
        "hourly_rate": "50",
        "open_time": "09:00:00",
        "close_time": "18:00:00",
        "spot_description": "Spacious and secure.",
        "available_days": "Monday,Tuesday,Friday",
        "verification_status": "3",
        "image": [base64_img1, base64_img2]
    }

      # If image is optional, we pass an empty list or None

    response = client.post("/spots/add-spot", data=data)

    assert response.status_code == 200
    assert response.json()['message'] == "Spot added successfully."

def test_invalid_spot(create_test_data):
    data = {
        "owner_id": "google-oauth2|1234567890",
        "spot_title": "Test Parking Spot",
        "spot_address": "456 Parking St",
        "latitude": "12.34",
        "longitude": "56.78",
        "available_slots": "3",
        "total_slots": "3",
        "hourly_rate": "50",
        "open_time": "09:00:00",
        "close_time": "18:00:00",
        # Missing spot_description
        # Missing available_days
        # Missing verification_status
    }

    response = client.post("/spots/add-spot", data=data)

    assert response.status_code == 422

def test_invalid_user_add_spot(create_test_data):
    data = {
        "owner_id": "google-oauth2|12345678901",
        "spot_title": "Test Parking Spot",
        "spot_address": "456 Parking St",
        "latitude": "12.34",
        "longitude": "56.78",
        "available_slots": "3",
        "total_slots": "3",
        "hourly_rate": "50",
        "open_time": "09:00:00",
        "close_time": "18:00:00",
        "spot_description": "Spacious and secure.",
        "available_days": "Monday,Tuesday,Friday",
        "verification_status": "3",
        
    }

    response = client.post("/spots/add-spot", data=data)

    assert response.status_code == 400 
  


