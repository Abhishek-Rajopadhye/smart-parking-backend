# app/core/oauth.py

import httpx
from fastapi import HTTPException
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_oauth_token(provider: str, code: str) -> dict:
    """
    Exchange OAuth2 code for an access token.

    Parameters:
        provider (str): The OAuth provider (e.g., 'google', 'github')
        code (str): The authorization code received from the OAuth provider

    Returns:
        dict: The access token and other related information

    Raises:
        HTTPException:
            400: If the provider is unsupported or the token exchange fails
            500: Any other error occurs during the process
    """
    provider_config = {
        "google": {
            "token_url": "https://oauth2.googleapis.com/token",
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        },
        "github": {
            "token_url": "https://github.com/login/oauth/access_token",
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "redirect_uri": settings.GITHUB_REDIRECT_URI,
        }
    }

    if provider not in provider_config:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                provider_config[provider]["token_url"],
                data={
                    "client_id": provider_config[provider]["client_id"],
                    "client_secret": provider_config[provider]["client_secret"],
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": provider_config[provider]["redirect_uri"],
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to obtain access token")

            return response.json()
    except httpx.HTTPError as http_error:
        raise HTTPException(status_code=500, detail=f"HTTP error occurred: {str(http_error)}")
    except Exception as general_error:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(general_error)}")

async def get_oauth_user_info(provider: str, access_token: str) -> dict:
    """
    Fetch user details from OAuth2 provider.

    Parameters:
        provider (str): The OAuth provider (e.g., 'google', 'github')
        access_token (str): The access token received from the OAuth provider

    Returns:
        dict: The user's profile information

    Raises:
        HTTPException:
            400: If fetching user info fails
            500: Any other error occurs during the process
    """
    provider_config = {
        "google": {
            "token_url": "https://oauth2.googleapis.com/token",
            "auth_url": "https://accounts.google.com/o/oauth2/auth",
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        },
        "github": {
            "token_url": "https://github.com/login/oauth/access_token",
            "auth_url": "https://github.com/login/oauth/authorize",
            "client_id": settings.GITHUB_CLIENT_ID,
            "userinfo_url": "https://api.github.com/user",
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "redirect_uri": settings.GITHUB_REDIRECT_URI,
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                provider_config[provider]["userinfo_url"],
                headers={"Authorization": f"Bearer {access_token}"}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch user info")

            return response.json()
    except httpx.HTTPError as http_error:
        raise HTTPException(status_code=500, detail=f"HTTP error occurred: {str(http_error)}")
    except HTTPException as http_exception:
        raise http_exception
    except Exception as general_error:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(general_error)}")