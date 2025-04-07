from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.booking_service import create_booking, get_bookings, get_booking_by_user, get_booking_by_spot, get_bookings_of_spots_of_owner, cancel_booking, check_in_booking, check_out_booking
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

@router.delete("/{booking_id}")
async def cancel_spot_booking(booking_id: str, db: Session = Depends(get_db)):
    """
    Cancel a specific spot booking.

    Parameters:
        booking_id (str): The ID of the booking to be canceled.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        dict: Response data otherwise raise appropriate HTTPException and return the error message
    """
    try:
        response = await cancel_booking(db, booking_id)
        return response
    except Exception as exception:
        print(exception)
        raise HTTPException(status_code=500, detail="Failed to cancel the booking")


@router.put("/checkin/{booking_id}")
async def check_in_spot_booking(booking_id: str, db: Session = Depends(get_db)):
    """
    Check in for a specific booking.

    Parameters:
        booking_id (str): The ID of the booking to check in.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        dict: Response data indicating success or failure of the check-in process.

    Example:
        check_in_spot_booking("123")
        check in for the booking with ID "123"
        return success or failure response
    """
    try:
        response = await check_in_booking(db, booking_id)
        return response
    except Exception as exception:
        print(exception)
        raise HTTPException(status_code=500, detail="Failed to check in for the booking")


@router.put("/checkout/{booking_id}")
async def check_out_spot_booking(booking_id: str, db: Session = Depends(get_db)):
    """
    Check out for a specific booking.

    Parameters:
        booking_id (str): The ID of the booking to check out.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        dict: Response data indicating success or failure of the check-out process.

    Example:
        check_out_spot_booking("123")
        check out for the booking with ID "123"
        return success or failure response
    """
    try:
        response = await check_out_booking(db, booking_id)
        return response
    except Exception as exception:
        print(exception)
        raise HTTPException(status_code=500, detail="Failed to check out for the booking")