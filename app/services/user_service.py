# app/services/user_service.py

from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.db.payment_model import Payment
from app.db.booking_model import Booking
from app.db.spot_model import Spot
from app.db.session import get_db
from app.db.oauth_model import OAuthUser
from app.schemas.user import UserProfile, UserUpdate, OwnerProfile
from app.core.oauth import oauth2_scheme
from app.services.auth_service import verify_oauth_token

class AuthenticationError(Exception):
    """Raised when invalid token or unauthorized access."""

    def __init__(self, message="Unauthorized Access."):
        self.message = message
        super().__init__(self.message)

async def get_profile_data(user_id: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        user = db.query(OAuthUser).filter(
            OAuthUser.provider_id == user_id).first()
        if not user:
            raise KeyError("User not found")

        payload = verify_oauth_token(token, provider=user.provider)
        if not payload:
            raise AuthenticationError("Invalid token")

        # Calculate total earnings
        total_earnings = (
            db.query(func.sum(Payment.amount))
            .join(Booking, Payment.id == Booking.payment_id)
            .join(Spot, Booking.spot_id == Spot.spot_id)
            .filter(Spot.owner_id == user_id)
            .scalar()
        ) or 0  # Default to 0 if no earnings

        return UserProfile(
            id=user.provider_id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            total_earnings=total_earnings,
            profile_picture=user.profile_picture
        )
    except KeyError as usernotfoundError:
        raise usernotfoundError
    except AuthenticationError as invalid_token:
        raise invalid_token
    except ValueError as value_error:
        raise value_error
    except TypeError as type_error:
        raise type_error
    except Exception as general_error:
        raise general_error


async def update_profile_details(user_id: str, user_update: UserUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
        user = db.query(OAuthUser).filter(
            OAuthUser.provider_id == user_id).first()
        if not user:
            raise KeyError("User not found")

        payload = verify_oauth_token(token, provider=user.provider)
        if not payload:
            raise AuthenticationError(status_code=401, detail="Invalid token")

        if user_update.name is not None:
            user.name = user_update.name
        if user_update.email is not None:
            user.email = user_update.email
        if user_update.phone is not None:
            user.phone = user_update.phone
        if user_update.profile_picture is not None:
            user.profile_picture = user_update.profile_picture

        db.commit()
        db.refresh(user)

        return UserProfile(
            id=user.provider_id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            profile_picture=user.profile_picture,
            total_earnings=user_update.total_earnings
        )
    except KeyError as notfound_error:
        raise notfound_error
    except ValueError as value_error:
        raise value_error
    except TypeError as type_error:
        raise type_error
    except AuthenticationError as auth_error:
        raise auth_error
    except Exception as general_error:
        raise general_error


async def get_profile_unauth(user_id: str, db: Session = Depends(get_db)):
    """
    Fetch un-authenticated user profile.

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
        user = db.query(OAuthUser).filter(
            OAuthUser.provider_id == user_id).first()
        if not user:
            raise KeyError("User not found")

        return OwnerProfile(
            id=user.provider_id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            profile_picture=user.profile_picture
        )
    except KeyError as notfound_error:
        raise notfound_error
    except Exception as general_error:
        raise general_error
