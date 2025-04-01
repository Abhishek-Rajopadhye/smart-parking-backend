from sqlalchemy.orm import Session
from app.db.oauth_model import OAuthUser
from tests.test_config import client, db

# Helper function to create a mock OAuth user
def create_mock_oauth_user(db: Session, provider: str, provider_id: str, email: str):
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
        provider=provider,
        provider_id=provider_id,
        email=email,
        name="Test User",
        profile_picture="http://example.com/avatar.png",
        access_token="mock_access_token"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Invalid Case 1: Invalid provider for login
def test_invalid_provider_login():
    """
    Test login with an invalid provider.

    Assertions:
        - The response status code is 400 (Bad Request).
        - The response JSON contains the detail "Invalid provider".
    """
    response = client.get("/api/v1/auth/invalid_provider/login")
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid provider"}

# Invalid Case 2: Missing authorization code in callback
def test_missing_authorization_code():
    """
    Test the callback with a missing authorization code.

    Assertions:
        - The response status code is 401 (Unauthorized).
        - The response JSON contains the detail "Authorization code not provided".
    """
    response = client.get("/api/v1/auth/google/callback")
    assert response.status_code == 401
    assert response.json() == {"detail": "Authorization code not provided"}
