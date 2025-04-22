import pytest
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.spot_model import Spot, Document
from app.db.oauth_model import OAuthUser
from tests.test_config import client, db, clean_test_db

# Helper to create a user, spot, and documents for verification
def create_spot_with_documents(db: Session, spot_id: int, owner_id: str, validation_status: int = 0):
    user = OAuthUser(
        provider="google",
        provider_id=owner_id,
        email=f"{owner_id}@example.com",
        name="Test User",
        profile_picture="http://example.com/avatar.png",
        access_token="mock_token"
    )
    db.add(user)
    db.commit()

    spot = Spot(
        spot_id=spot_id,
        owner_id=owner_id,
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
        image=b"mock_image_data",
        created_at=datetime.now(),
        validation_status=validation_status
    )
    db.add(spot)
    db.commit()

    doc_types = ["identity_proof", "ownership_proof", "supporting_document"]
    for i, doc_type in enumerate(doc_types):
        doc = Document(
            spot_id=spot_id,
            filename=f"{doc_type}.pdf",
            document_type=doc_type,
            content=b"fakepdfdata",
            uploaded_at=datetime.now()
        )
        db.add(doc)
    db.commit()
    return spot

# 1. Test: Get pending verification requests (success)
def test_get_pending_verification_requests(db):
    create_spot_with_documents(db, spot_id=1, owner_id="owner1")
    response = client.get("/api/v1/verification/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["spot_id"] == 1
    assert data[0]["identity_proof_document"]["file_name"] == "identity_proof.pdf"

# 2. Test: Get pending verification requests (none found)
def test_get_pending_verification_requests_none(db):
    response = client.get("/api/v1/verification/")
    assert response.status_code == 404
    assert "No pending verification requests found" in response.json()["detail"]

# 3. Test: Accept verification request (success)
def test_accept_verification_request(db):
    create_spot_with_documents(db, spot_id=2, owner_id="owner2")
    response = client.put("/api/v1/verification/request/accept/2")
    assert response.status_code == 200
    assert response.json()["validation_status"] == 1

# 4. Test: Accept verification request (spot not found)
def test_accept_verification_request_not_found(db):
    response = client.put("/api/v1/verification/request/accept/9999")
    assert response.status_code == 404

# 5. Test: Reject verification request (success)
def test_reject_verification_request(db):
    create_spot_with_documents(db, spot_id=3, owner_id="owner3")
    response = client.put("/api/v1/verification/request/reject/3")
    assert response.status_code == 200
    assert response.json()["validation_status"] == -1

# 6. Test: Reject verification request (spot not found)
def test_reject_verification_request_not_found(db):
    response = client.put("/api/v1/verification/request/reject/8888")
    assert response.status_code == 404

# 7. Test: Documents are sorted into correct fields
def test_documents_sorted_into_fields(db):
    create_spot_with_documents(db, spot_id=4, owner_id="owner4")
    response = client.get("/api/v1/verification/")
    assert response.status_code == 200
    data = response.json()
    found = False
    for spot in data:
        if spot["spot_id"] == 4:
            found = True
            assert spot["identity_proof_document"]["file_type"] == "identity_proof"
            assert spot["ownership_proof_document"]["file_type"] == "ownership_proof"
            assert spot["supporting_document"]["file_type"] == "supporting_document"
    assert found