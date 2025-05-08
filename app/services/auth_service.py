# app/services/auth_service.py

from sqlalchemy.orm import Session
from app.db.oauth_model import OAuthUser
from typing import Optional, Literal
import requests


def verify_google_token(token: str) -> Optional[dict]:
    """
    Verify a Google OAuth token by calling Google's tokeninfo endpoint.

    Parameters:
        token (str): The Google OAuth token to verify

    Returns:
        Optional[dict]: User information if token is valid, None otherwise

    Raises:
        requests.RequestException: If there is an error with the request
        ValueError: If the response cannot be parsed as JSON
    """
    try:
        # Google's token verification endpoint
        tokeninfo_url = f"https://oauth2.googleapis.com/tokeninfo?access_token={token}"

        # Send request to Google's API
        response = requests.get(tokeninfo_url)

        # Check if request was successful
        if response.status_code == 200:
            user_info = response.json()
            return {
                "provider": "google",
                "user_id": user_info.get("sub"),
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "picture": user_info.get("picture"),
                "raw_info": user_info
            }
        else:
            print(
                f"Google token verification failed: {response.status_code}, {response.text}")
            return None
    except requests.RequestException as request_error:
        print(f"Google token verification request error: {request_error}")
        raise request_error
    except ValueError as value_error:
        print(f"Google token verification value error: {value_error}")
        raise value_error


def verify_github_token(token: str) -> Optional[dict]:
    """
    Verify a GitHub OAuth token by calling GitHub's user API endpoint.

    Parameters:
        token (str): The GitHub OAuth token to verify

    Returns:
        Optional[dict]: User information if token is valid, None otherwise

    Raises:
        requests.RequestException: If there is an error with the request
        ValueError: If the response cannot be parsed as JSON
    """
    try:
        # GitHub's user API endpoint
        user_url = "https://api.github.com/user"
        email_url = "https://api.github.com/user/emails"

        # Set up headers with the token
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

        # Get user info
        user_response = requests.get(user_url, headers=headers)

        if user_response.status_code != 200:
            print(
                f"GitHub token verification failed: {user_response.status_code}, {user_response.text}")
            return None

        user_info = user_response.json()

        # Get email (might be private, so we need a separate call)
        email_response = requests.get(email_url, headers=headers)
        email = None

        if email_response.status_code == 200:
            emails = email_response.json()
            # Find primary email
            for email_obj in emails:
                if email_obj.get("primary"):
                    email = email_obj.get("email")
                    break

        return {
            "provider": "github",
            "user_id": str(user_info.get("id")),
            "email": email,
            "name": user_info.get("name"),
            "login": user_info.get("login"),
            "picture": user_info.get("avatar_url"),
            "raw_info": user_info
        }
    except requests.RequestException as request_error:
        print(f"GitHub token verification request error: {request_error}")
        raise request_error
    except ValueError as value_error:
        print(f"GitHub token verification value error: {value_error}")
        raise value_error


def verify_oauth_token(token: str, provider: Literal["google", "github"] = None) -> Optional[dict]:
    """
    Verify an OAuth token from either Google or GitHub.

    Parameters:
        token (str): The OAuth token to verify
        provider (str, optional): The provider ("google" or "github"). If not provided, will attempt to detect.

    Returns:
        Optional[dict]: User information if token is valid, None otherwise

    Raises:
        KeyError: If invalid OAuth provider is specified
        ValueError: If the response cannot be parsed as JSON
        requests.RequestException: If there is an error with the request
    """
    # If provider is specified, use the appropriate verification
    try:
        if provider == "google":
            return verify_google_token(token)
        elif provider == "github":
            return verify_github_token(token)
        else:
            raise KeyError("Invalid OAuth provider")
    except KeyError as invalidOAuthProvider:
        raise invalidOAuthProvider
    except ValueError as value_error:
        raise value_error
    except requests.RequestException as request_error:
        raise request_error


def get_user_by_provider_id(db: Session, provider: str, provider_id: str):
    """
    Fetch a user by provider and provider ID.

    Parameters:
        db (Session): The database session
        provider (str): The OAuth provider (e.g., 'google', 'github')
        provider_id (str): The provider ID of the user

    Returns:
        OAuthUser: The user object if found, None otherwise
    """
    return db.query(OAuthUser).filter(OAuthUser.provider == provider, OAuthUser.provider_id == provider_id).first()


def create_oauth_user(db: Session, user_data: dict):
    """
    Create a new OAuth user or update an existing one.

    Parameters:
        db (Session): The database session
        user_data (dict): The user data to create or update

    Returns:
        OAuthUser: The created or updated user object
    """
    new_user = OAuthUser(
    provider='google',
    provider_id='google-oauth2|1234567890',
    email='johndoe@gmail.com',
    name='John Doe',
    phone='1234567890',
    profile_picture='https://example.com/images/johndoe.jpg',
    access_token='ya29.a0AfH6SMCuK_token_example_1',
    refresh_token='1//0g_example_refresh_token'
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    user = get_user_by_provider_id(
        db, user_data["provider"], user_data["provider_id"])

    if user:
        user.access_token = user_data["access_token"]
        db.commit()
        return user

    new_user = OAuthUser(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
