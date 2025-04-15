import razorpay
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.booking_model import Booking
from app.db.payment_model import Payment
from app.db.oauth_model import OAuthUser
from app.db.spot_model import Spot
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

# Load Razorpay keys
RAZORPAY_KEY_ID = settings.RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET = settings.RAZORPAY_KEY_SECRET

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Custom Exceptions


class SlotUnavailableException(Exception):
    """Raised when no slots are available for booking."""

    def __init__(self, message="No slots available for booking."):
        self.message = message
        super().__init__(self.message)


class PaymentFailedException(Exception):
    """Raised when the payment process fails."""

    def __init__(self, message="Payment process failed. Please try again."):
        self.message = message
        super().__init__(self.message)


class BookingFailedException(Exception):
    """Raised when booking cannot be completed."""

    def __init__(self, message="Booking process failed. Please contact support."):
        self.message = message
        super().__init__(self.message)


# Check slot availability before processing payment
def check_available_slots(db: Session, spot_id: int, total_slots: int):
    """
    Check if the required number of slots are available for booking.

    Parameters:
        db (Session): SQLAlchemy database session
        spot_id (int): Spot ID
        total_slots (int): Number of slots to book

    Returns:
        bool: True if slots are available, False otherwise

    Example:
        check_available_slots(db, 1, 2)
        checking if 2 slots are available for spot ID 1
        slots are available, return True otherwise return False
    """
    try:
        query = text("SELECT * FROM spots WHERE spot_id = :spot_id")
        result = db.execute(query, {"spot_id": spot_id})
        spot = result.fetchone()

        if not spot:
            raise SlotUnavailableException("Spot not found.")

        available_slots = spot.available_slots
        if available_slots >= total_slots:
            # Update available slots
            query = text(
                "UPDATE spots SET available_slots = available_slots - :total_slots WHERE spot_id = :spot_id"
            )
            db.execute(query, {"spot_id": spot_id, "total_slots": total_slots})
            db.commit()
            return True
        else:
            return False

    except SlotUnavailableException as slot_error:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(slot_error))

    except Exception as db_error:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(db_error)}")

# Create a new booking


async def create_booking(db: Session, booking_data):
    """
    Create a new booking for the user and add the details to the database.
    first check if the required number of slots are available for booking.
    then create a Razorpay order for the payment.
    store the payment info in the database.
    simulate payment verification and store the booking details in the database.
    Add the booking details to the database.

    Parameters:
        db (Session): SQLAlchemy database session
        booking_data (BookingCreate): Booking data

    Returns:
        dict: Booking details

    Example:
        create_booking(db, booking_data)
        create a new booking with the given booking data
        return booking details else raise an exception
    """
    try:
        print("This is in service model")

        db.begin()

        slot = db.execute(text(
            "SELECT * FROM spots WHERE spot_id = :spot_id AND available_slots >= :total_slots FOR UPDATE"),
            {"spot_id": booking_data.spot_id,
                "total_slots": booking_data.total_slots}
        ).fetchone()

        if not slot:
            raise HTTPException(status_code=400, detail="No Slot Available")
        print("after not slot")
        try:
            order_data = {
                "amount": booking_data.total_amount * 100,  # Convert INR to paise
                "currency": "INR",
                "receipt": f"receipt_{booking_data.user_id}",
                "payment_capture": 1  # Auto capture
            }
            print("before razorpay order")
            razorpay_order = razorpay_client.order.create(order_data)
            print("after razorpay order")
        except Exception as payment_error:
            db.rollback()
            raise HTTPException(
                status_code=402, detail=f"Failed to create Razorpay order: {str(payment_error)}")

        new_payment = Payment(
            user_id=booking_data.user_id,
            spot_id=booking_data.spot_id,
            amount=booking_data.total_amount,
            razorpay_order_id=razorpay_order["id"],
            status="pending"
        )
        print(new_payment)
        print("Payment init")
        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)

        # Simulating a successful payment (should be dynamic)
        # payment_status = "success"

        # if payment_status == "success":
        #     new_payment.status = "success"
        #     new_booking = Booking(
        #     user_id=booking_data.user_id,
        #     spot_id=booking_data.spot_id,
        #     total_slots=booking_data.total_slots,
        #     start_date_time=booking_data.start_date_time,
        #     end_date_time=booking_data.end_date_time,
        #     payment_id=new_payment.id
        # )
        #     db.add(new_booking)
        db.execute(text(
        "UPDATE spots SET available_slots = available_slots - :total_slots WHERE spot_id = :spot_id"),
        {"spot_id": booking_data.spot_id,
        "total_slots": booking_data.total_slots}
        )
        db.commit()  # Update payment status
        # else:
        #     new_payment.status = "failed"
        #     db.commit()
        #     db.rollback()
        #     raise HTTPException(
        #         status_code=402, detail="Payment verification failed.")
        print("after payment commit")
        return {
            "order_id": razorpay_order["id"],
            "amount": razorpay_order["amount"],
            "currency": razorpay_order["currency"],
            "payment_id": new_payment.id,
            "payment_status": "pending",
            "receipt": razorpay_order["receipt"]
        }

    except HTTPException as http_error:
        db.rollback()
        raise HTTPException(status_code=402, detail=str(
            payment_error))  # 402 Payment Required
    except BookingFailedException as booking_error:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(booking_error))
    except IntegrityError as db_error:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(db_error)}")
    except Exception as unexpected_error:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {str(unexpected_error)}")

async def update_booking(db: Session, payment_data: Payment):
    """
    Update the payment status, create booking, and update spot availability.
    """
    try:
        print("Hi..")
        print("This is in update booking service model")

        # Start a transaction block
        payment = db.query(Payment).filter(Payment.id == payment_data.payment_id).with_for_update().one_or_none()

        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found.")

        # Update payment details
        payment.status = "success"
        payment.razorpay_signature = payment_data.razorpay_signature
        payment.razorpay_payment_id = payment_data.razorpay_payment_id
        db.commit()
        db.refresh(payment)

        print("Payment updated successfully")

        # Create booking only if payment is successful
        if payment.status == "success":
            print("Creating booking")

            # Lock the Spot row to prevent race condition
            spot = db.query(Spot).filter(Spot.spot_id == payment.spot_id).with_for_update().one_or_none()

            if not spot:
                raise HTTPException(status_code=404, detail="Spot not found.")

            # if spot.available_slots < payment_data.total_slots:
                # raise HTTPException(status_code=400, detail="Not enough slots available.")

            booking = Booking(
                user_id=payment.user_id,
                spot_id=payment.spot_id,
                start_date_time=payment_data.start_time,
                end_date_time=payment_data.end_time,
                payment_id=payment.id,
                total_slots=payment_data.total_slots,
                status="Pending"
            )

            db.add(booking)
            # Update the available slots atomically
            #spot.available_slots -= booking.total_slots

            db.commit()
            db.refresh(booking)

            print("Booking created successfully")

        return {
            "payment_status": payment.status,
            "razorpay_signature": payment.razorpay_signature,
            "razorpay_order_id": payment.razorpay_order_id
        }

    except HTTPException as http_err:
        db.rollback()
        print("Handled error:", http_err.detail)
        raise http_err
    except Exception as e:
        db.rollback()
        print("Unhandled error:", str(e))
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your booking.")
    finally:
        try:
            if not (payment and payment.status == "success"):
                # db.execute(text(
                #     "UPDATE spots SET available_slots = available_slots + :total_slots WHERE spot_id = :spot_id"),
                #     {"spot_id": payment_data.spot_id,
                #     "total_slots": payment_data.total_slots}
                # )
                spot.available_slots += payment_data.total_slots
                db.commit()
        except Exception as e:
            print("Error during slot release in finally block:", str(e))
        finally:
            db.close()


async def get_bookings(db: Session):
    """
    Retrieve all bookings from the database with additional fields from Spot and Payment tables.

    Parameters:
        db (Session): SQLAlchemy database session

    Returns:
        List[dict]: List of all bookings with additional fields

    Example:
        get_bookings(db)
        retrieve all bookings from the database
        return list of all bookings with additional fields
    """
    try:
        bookings = (
            db.query(
                Booking,
                Spot.spot_title,
                Spot.address.label("spot_address"),
                Payment.amount,
                Payment.status.label("payment_status")
            )
            .join(Spot, Booking.spot_id == Spot.spot_id)
            .join(Payment, Booking.payment_id == Payment.id)
            .all()
        )

        return [
            {
                "id": booking.Booking.id,
                "user_id": booking.Booking.user_id,
                "spot_id": booking.Booking.spot_id,
                "spot_title": booking.spot_title,
                "spot_address": booking.spot_address,
                "total_slots": booking.Booking.total_slots,
                "start_date_time": booking.Booking.start_date_time,
                "end_date_time": booking.Booking.end_date_time,
                "payment_id": booking.Booking.payment_id,
                "payment_amount": booking.amount,
                "payment_status": booking.payment_status,
                "status": booking.Booking.status
            }
            for booking in bookings
        ]
    except Exception as db_error:
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(db_error)}")


async def get_booking_by_user(db: Session, user_id: int):
    """
    Retrieve all bookings for a specific user with additional fields from Spot and Payment tables.

    Parameters:
        db (Session): SQLAlchemy database session
        user_id (int): User ID

    Returns:
        List[dict]: List of bookings for the specified user with additional fields

    Example:
        get_booking_by_user(db, 1)
        retrieve all bookings for user ID 1
        return list of bookings for the user with additional fields
    """
    try:
        bookings = (
            db.query(
                Booking,
                Spot.spot_title,
                Spot.address.label("spot_address"),
                Payment.amount,
                Payment.status.label("payment_status")
            )
            .join(Spot, Booking.spot_id == Spot.spot_id)
            .join(Payment, Booking.payment_id == Payment.id)
            .filter(Booking.user_id == str(user_id))
            .all()
        )

        return [
            {
                "id": booking.Booking.id,
                "user_id": booking.Booking.user_id,
                "spot_id": booking.Booking.spot_id,
                "spot_title": booking.spot_title,
                "spot_address": booking.spot_address,
                "total_slots": booking.Booking.total_slots,
                "start_date_time": booking.Booking.start_date_time,
                "end_date_time": booking.Booking.end_date_time,
                "payment_id": booking.Booking.payment_id,
                "payment_amount": booking.amount,
                "payment_status": booking.payment_status,
                "status": booking.Booking.status
            }
            for booking in bookings
        ]
    except Exception as db_error:
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(db_error)}")


async def get_booking_by_spot(db: Session, spot_id: int):
    """
    Retrieve all bookings for a specific spot with additional fields from Spot and Payment tables.

    Parameters:
        db (Session): SQLAlchemy database session
        spot_id (int): Spot ID

    Returns:
        List[dict]: List of bookings for the specified spot with additional fields

    Example:
        get_booking_by_spot(db, 1)
        retrieve all bookings for spot ID 1
        return list of bookings for the spot with additional fields
    """
    try:
        bookings = (
            db.query(
                Booking,
                OAuthUser.name.label("user_name"),
                Spot.spot_title,
                Spot.address.label("spot_address"),
                Payment.amount,
                Payment.status.label("payment_status")
            )
            .join(Spot, Booking.spot_id == Spot.spot_id)
            .join(Payment, Booking.payment_id == Payment.id)
            .join(OAuthUser, Booking.user_id == OAuthUser.provider_id)  # Corrected join
            .filter(Booking.spot_id == spot_id)
            .all()
        )

        return [
            {
                "id": booking.Booking.id,
                "user_id": booking.Booking.user_id,
                "user_name": booking.user_name,
                "spot_id": booking.Booking.spot_id,
                "spot_title": booking.spot_title,
                "spot_address": booking.spot_address,
                "total_slots": booking.Booking.total_slots,
                "start_date_time": booking.Booking.start_date_time,
                "end_date_time": booking.Booking.end_date_time,
                "payment_id": booking.Booking.payment_id,
                "payment_amount": booking.amount,
                "payment_status": booking.payment_status,
                "status": booking.Booking.status
            }
            for booking in bookings
        ]
    except Exception as db_error:
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(db_error)}")


async def get_bookings_of_spots_of_owner(db: Session, user_id: int):
    """
    Retrieve all bookings for the spots of a specific owner with additional fields from Spot and Payment tables.

    Parameters:
        db (Session): SQLAlchemy database session
        user_id (int): User ID

    Returns:
        List[dict]: List of bookings for the spots of the specified owner with additional fields

    Example:
        get_bookings_of_spots_of_owner(db, 1)
        retrieve all bookings for the spots of owner ID 1
        return list of bookings for the spots of the owner with additional fields
    """
    try:
        bookings = (
            db.query(
                Booking,
                Spot.spot_title,
                Spot.address.label("spot_address"),
                Payment.amount,
                Payment.status.label("payment_status")
            )
            .join(Spot, Booking.spot_id == Spot.spot_id)
            .join(Payment, Booking.payment_id == Payment.id)
            .filter(Spot.owner_id == str(user_id))
            .all()
        )

        return [
            {
                "id": booking.Booking.id,
                "user_id": booking.Booking.user_id,
                "spot_id": booking.Booking.spot_id,
                "spot_title": booking.spot_title,
                "spot_address": booking.spot_address,
                "total_slots": booking.Booking.total_slots,
                "start_date_time": booking.Booking.start_date_time,
                "end_date_time": booking.Booking.end_date_time,
                "payment_id": booking.Booking.payment_id,
                "payment_amount": booking.amount,
                "payment_status": booking.payment_status,
                "status": booking.Booking.status
            }
            for booking in bookings
        ]
    except Exception as db_error:
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(db_error)}")


async def cancel_booking(db: Session, booking_id):
    """
    Cancel a booking by updating its status to "Cancelled" in the database.

    Parameters:
        db (Session): SQLAlchemy database session
        booking_id (int): The ID of the booking to be cancelled

    Returns:
        int: The number of rows updated in the database (should be 1 if successful)

    Example:
        cancel_booking(db, 123)
        cancel the booking with ID 123 by setting its status to "Cancelled"
        return the number of rows updated
    """
    try:
        db.query(Booking).filter(Booking.id == str(booking_id)).update({
            "status": "Cancelled"
        })
        booking = db.query(Booking).filter(Booking.id == str(booking_id)).one()
        spot = db.query(Spot).filter(Booking.id == str(booking_id)).filter(
            Booking.spot_id == Spot.spot_id).one()
        db.query(Spot).filter(Booking.id == str(booking_id)).filter(Booking.spot_id == Spot.spot_id).update({
            "available_slots": spot.available_slots + booking.total_slots
        })
        db.commit()
        return booking
    except Exception as db_error:
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(db_error)}")


async def check_in_booking(db: Session, booking_id):
    """
    Check in a booking by updating its status to "Checked In" in the database.

    Parameters:
        db (Session): SQLAlchemy database session
        booking_id (int): The ID of the booking to be checked in

    Returns:
        int: The number of rows updated in the database (should be 1 if successful)

    Example:
        check_in_booking(db, 123)
        check in the booking with ID 123 by setting its status to "Checked In"
        return the number of rows updated
    """
    try:
        booking = db.query(Booking).filter(Booking.id == str(booking_id)).update({
            "status": "Checked In"
        })
        db.commit()
        return booking
    except Exception as db_error:
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(db_error)}")


async def check_out_booking(db: Session, booking_id):
    """
    Check out a booking by updating its status to "Completed" in the database.

    Parameters:
        db (Session): SQLAlchemy database session
        booking_id (int): The ID of the booking to be checked out

    Returns:
        int: The number of rows updated in the database (should be 1 if successful)

    Example:
        check_out_booking(db, 123)
        check out the booking with ID 123 by setting its status to "Completed"
        return the number of rows updated
    """
    try:
        db.query(Booking).filter(Booking.id == str(booking_id)).update({
            "status": "Completed"
        })

        booking = db.query(Booking).filter(Booking.id == str(booking_id)).one()
        spot = db.query(Spot).filter(Booking.id == str(booking_id)).filter(
            Booking.spot_id == Spot.spot_id).one()
        db.query(Spot).filter(Booking.id == str(booking_id)).filter(Booking.spot_id == Spot.spot_id).update({
            "available_slots": spot.available_slots + booking.total_slots
        })
        db.commit()
        return booking
    except Exception as db_error:
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(db_error)}")
    
async def update_available_slots(db: Session, booking_data):
    """
    Update the booking slots for a specific booking.

    Parameters:
        db (Session): SQLAlchemy database session
        booking_data (BookingUpdate): Booking data

    Returns:
        dict: Updated booking details

    Example:
        update_booking(db, booking_data)
        update the booking with the given booking data
        return updated booking details else raise an exception
    """
    try:
        spot = db.query(Spot).filter(Spot.spot_id == booking_data.spot_id).with_for_update().one_or_none()
        spot.available_slots += booking_data.total_slots
        db.commit()
        return {"message": "Booking updated successfully"}
    except Exception as db_error:
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(db_error)}")
