from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.booking_service import create_booking, get_bookings, get_booking_by_user, get_booking_by_spot, get_bookings_of_spots_of_owner
from app.schemas.booking import BookingCreate

router = APIRouter()

@router.get("/")
async def get_booking(db: Session = Depends(get_db)):
    """
    Retrieve all bookings

    Parameters:
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        List[dict]: List of all bookings
    """
    return await get_bookings(db)

@router.get("/user/{user_id}")
async def get_booking_by_user_id(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all bookings for a specific user.

    Parameters:
        user_id (int): User ID
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        List[Booking]: List of bookings for the specified user
    """
    return await get_booking_by_user(db, user_id)

@router.get("/owner/{user_id}")
async def get_booking_of_spots_of_owner(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all bookings of spots owned by a specific user.

    Parameters:
        user_id (int): User ID
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        List[dict]: List of bookings for the specified user
    """
    return await get_bookings_of_spots_of_owner(db, user_id)

@router.get("/spot/{spot_id}")
async def get_booking_by_spot_id(spot_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all bookings for a specific spot.

    Parameters:
        spot_id (int): Spot ID
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        List[dict]: List of bookings for the specified spot
    """
    return await get_booking_by_spot(db, spot_id)

@router.post("/book-spot")
async def book_spot(booking_data: BookingCreate, db: Session = Depends(get_db)):
    """
    Book a parking spot for the user.

    Parameters:
        booking_data (BookingCreate): Booking data
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        dict: Response message otherwise raise appropriate HTTPException and return the error message

    Example:
        book_spot(booking_data)
        booking a parking spot for the user
        return the booking details
    """
    try:
        print(booking_data.__dict__)
        response = await create_booking(db, booking_data)
        # print(response)
        if "error" in response:
            raise HTTPException(status_code=400, detail=response["detail"])
        return response
    except Exception as exception:
        print(exception)
        raise HTTPException(status_code=400, detail="Failed to book the spot")