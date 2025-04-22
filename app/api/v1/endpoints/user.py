# app/api/v1/endpoints/user.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.user_service import get_profile_data, update_profile_details, get_profile_unauth
from app.db.session import get_db
from app.schemas.user import UserProfile, UserUpdate, OwnerProfile
from app.core.oauth import oauth2_scheme

router = APIRouter()


class AuthenticationError(Exception):
    """Raised when invalid token or unauthorized access."""

    def __init__(self, message="Unauthorized Access."):
        self.message = message
        super().__init__(self.message)


@router.get("/profile/{user_id}", response_model=UserProfile)
async def get_profile(user_id: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Fetch authenticated user profile.

    Parameters:
        user_id (str): The ID of the user
        token (str): The OAuth2 token
        db (Session): The database session

    Returns:
        UserProfile: The user's profile information

    Raises:
        HTTPException: 
            404: If the user is not found
            401: If the token is invalid
            500: Any other error occurs during the process
    """
    try:
        return await get_profile_data(user_id, token, db)
    except KeyError as notfound_error:
        raise HTTPException(status_code=404, detail=notfound_error)
    except ValueError as value_error:
        raise HTTPException(
            status_code=500, detail=f"Value error: {str(value_error)}")
    except TypeError as type_error:
        raise HTTPException(
            status_code=500, detail=f"Type error: {str(type_error)}")
    except Exception as general_error:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(general_error)}")


@router.put("/profile/{user_id}", response_model=UserProfile)
async def update_profile(user_id: str, user_update: UserUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Update authenticated user profile.

    Parameters:
        user_id (str): The ID of the user
        user_update (UserUpdate): The user details to update
        token (str): The OAuth2 token
        db (Session): The database session

    Returns:
        UserProfile: The updated user's profile information

    Raises:
        HTTPException: 
            404: If the user is not found
            401: If the token is invalid
            500: Any other error occurs during the process
    """
    try:
        return await update_profile_details(user_id, user_update, token, db)
    except KeyError as keyError:
        raise HTTPException(status_code=404, detail=str(keyError))
    except AuthenticationError as unauthorized:
        raise HTTPException(status_code=401, detail=str(unauthorized))
    except ValueError as value_error:
        raise HTTPException(
            status_code=500, detail=f"Value error: {str(value_error)}")
    except TypeError as type_error:
        raise HTTPException(
            status_code=500, detail=f"Type error: {str(type_error)}")
    except Exception as general_error:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(general_error)}")


@router.get("/owner/{user_id}", response_model=OwnerProfile)
async def get_profile(user_id: str, db: Session = Depends(get_db)):
    """
    Fetch authenticated user profile.

    Parameters:
        user_id (str): The ID of the user
        db (Session): The database session

    Returns:
        UserProfile: The user's profile information

    Raises:
        HTTPException: 
            404: If the user is not found
    """
    try:
        return await get_profile_unauth(user_id, db)
    except KeyError as not_found_error:
        raise HTTPException(status_code=404, detail=str(not_found_error))
    except Exception as general_error:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(general_error)}")
