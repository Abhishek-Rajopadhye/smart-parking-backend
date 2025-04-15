from app.schemas.spot import AddSpot
from sqlalchemy.orm import Session
from app.db.spot_model import Spot
from fastapi import HTTPException
from sqlalchemy.sql import text
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
        image_blobs = []
        for image_b64 in (spot.image or []):
            image_data = base64.b64decode(image_b64)
            image_blobs.append(image_data)
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
            image=image_blobs
        )
        db.add(new_spot)
        db.commit()
        db.refresh(new_spot)
        return {"message": "Spot added successfully.", "spot_id": new_spot.spot_id}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400, detail="Error occur during adding spot.")

def get_spot_list_of_owner(user_id: int, db: Session):
    """
    Retrieve all spots owned by a specific user.

    Parameters:
        user_id (int): User ID
        db (Session): SQLAlchemy database session

    Returns:
        List[dict]: List of spots for the specified user
    """
    try:
        print("starting to fetch spots")
        spots = db.query(Spot).filter(Spot.owner_id == str(user_id)).all()
        if not spots:
            raise HTTPException(status_code=404, detail="No spots found for this owner.")
        query = text("select * from spots where owner_id = :user_id")
        result = db.execute(query, {"user_id": str(user_id)}).fetchall()
        spot_list = []
        print("before adding spots")
        
        for row in result:
            s = ""
            s += ", ".join(str(item) for item in row[12])
            total_earning = db.execute(
                text("select SUM(amount) from payments where spot_id = :spot_id"), 
                {"spot_id": row[0]}).fetchone()
            total_earning = 0 if total_earning[0] == None else total_earning[0] 
            spot_list.append({
                "id": row[0],
                "title": row[2],
                "description": row[11],
                "totalEarning": total_earning,
                "address": row[3],
                "openTime": row[9],
                "closeTime": row[10],
                "hourlyRate": row[6],
                "totalSlots": row[7],
                "openDays":  s
            })
        return spot_list
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Error occur during fetching spots.")