from app.schemas.spot import AddSpot
from sqlalchemy.orm import Session
from app.db.spot_model import Spot
from fastapi import HTTPException
import base64 

def add_spot(spot: AddSpot, db: Session):
    """
    Add a parking spot for the user.

    Parameters:
        spot_data (AddSpot): Spot data
        db (Session): SQLAlchemy database session

    Returns:
        dict: Response message

    Example:
        add_spot(db, spot_data)
        add a parking spot for the user
        return the spot details
    """
    try:
        #   print(spot)
        image_data = base64.b64decode(spot.image)
        new_spot = Spot(
            address=spot.spot_address,
            owner_id=spot.owner_id,
            spot_title=spot.spot_title,
            latitude=spot.latitude,
            longitude=spot.longitude,
            available_slots=spot.available_slots,
            no_of_slots=spot.total_slots,
            hourly_rate=spot.hourly_rate,
            open_time=spot.open_time,
            close_time=spot.close_time,
            description=spot.spot_description,
            available_days=spot.available_days,
            image=image_data
        )
        db.add(new_spot)
        db.commit()
        db.refresh(new_spot)
        return {"message": "Spot added successfully.", "spot_id": new_spot.spot_id}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Error occur during adding spot.")
