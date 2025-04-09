# app/api/v1/endpoints/auth.py
 
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from app.core.oauth import get_oauth_token, get_oauth_user_info
from app.db.session import get_db
from app.services.auth_service import create_oauth_user
from app.core.config import settings
 
router = APIRouter()
 
 
@router.get("/{provider}/login")
async def login(provider: str):
    """
    Redirect user to OAuth provider login page.
 
    Parameters:
        provider (str): The OAuth provider (e.g., 'google', 'github')
 
    Returns:
        RedirectResponse: Redirects to the OAuth provider's login page
 
    Raises:
        HTTPException:
            400: If the provider is invalid
            500: If an internal server error occurs
    """
    try:
        if provider not in ["google", "github"]:
            raise HTTPException(status_code=400, detail="Invalid provider")
 
        config = settings.model_dump()
        auth_url = (
            f"{config[f'{provider.upper()}_AUTH_URL']}?client_id={config[f'{provider.upper()}_CLIENT_ID'].strip()}"
            f"&redirect_uri={config[f'{provider.upper()}_REDIRECT_URI']}&response_type=code&scope=openid%20email%20profile"
        )
        return RedirectResponse(auth_url)
    except HTTPException as http_error:
        raise http_error
    except Exception as general_error:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(general_error)}")
 
 
@router.get("/{provider}/callback")
async def callback(provider: str, request: Request, db: Session = Depends(get_db)):
    """
    Handle OAuth2 callback.
 
    Parameters:
        provider (str): The OAuth provider (e.g., 'google', 'github')
        request (Request): The incoming request object
        db (Session): The database session
 
    Returns:
        RedirectResponse: Redirects to the dashboard with token and user_id
 
    Raises:
        HTTPException:
            401: If the authorization code is not provided
            400: If the access token cannot be obtained
            500: If an internal server error occurs
    """
    code = request.query_params.get("code")
    config = settings.model_dump()
 
    if not code:
        raise HTTPException(
            status_code=401, detail="Authorization code not provided")
 
    try:
        # Exchange code for token
        token_data = await get_oauth_token(provider, code)
        access_token = token_data.get("access_token")
 
        if not access_token:
            raise HTTPException(
                status_code=400, detail="Failed to obtain access token")
 
        # Get user info
        user_info = await get_oauth_user_info(provider, access_token)
 
        user_data = {
            "provider": provider,
            "provider_id": str(user_info.get("id")),
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "profile_picture": user_info.get("avatar_url") if provider == "github" else user_info.get("picture"),
            "access_token": access_token
        }
 
        # Save user in the database
        user = create_oauth_user(db, user_data)
        return RedirectResponse(f"{config["FRONTEND_URL"]}/auth?token={access_token}&user_id={user_data['provider_id']}")
 
    except HTTPException as http_error:
        raise http_error
    except Exception as general_error:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(general_error)}")
 