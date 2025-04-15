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
            raise HTTPException(
                status_code=404, detail="No spots found for this owner.")
        query = text("select * from spots where owner_id = :user_id")
        result = db.execute(query, {"user_id": str(user_id)}).fetchall()
        spot_list = []
        print("before adding spots")

        for row in result:
            s = ""
            s += ", ".join(str(item) for item in row[12])
            # print(row[12])
            # print(s)
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
            # print(spot_list[0]["openDays"])
        # print(spot_list[0])
        return spot_list
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400, detail="Error occur during fetching spots.")


async def update_spot_details(updated_spot, spot_id:int, db: Session):
    """
    Updates a spot with the given updated details.

    Parameters:
        updated_spot (dict): The dictionary containing the updated details of the spot
        db (Session): SQLAlchemy database session

    Raises:
        HTTPException (400): If there is less total_slots in updated spot, than current available_slots
        HTTPException (404): If the spot to update is not found
        HTTPException (500): If there is any issue updating the spot details

    Returns:
        dict: The updated spot
    """
    try:
        spot = db.query(Spot).filter(
            Spot.spot_id == spot_id).one()
        if (not spot or spot == None):
            raise HTTPException(status_code=404, detail="Spot not found")
        if (spot.available_slots > updated_spot.total_slots):
            raise HTTPException(
                status_code=400, detail="Slots are in use. Please try again when slots are empty.")
        db.query(Spot).filter(Spot.spot_id == updated_spot.spot_id).update(
            {
                "spot_title": updated_spot.spot_title,
                "address": updated_spot.address,
                "hourly_rate": updated_spot.hourly_rate,
                "no_of_slots": updated_spot.no_of_slots,
                "open_time": updated_spot.open_time,
                "close_time": updated_spot.close_time,
                "description": updated_spot.description,
                "available_days": updated_spot.available_days,
                "image": updated_spot.image
            })
        db.commit()
        return updated_spot
    except Exception as db_error:
        raise HTTPException(
            status_code=500, detail="Database Error" + str(db_error))


async def delete_spot(spot_id: int, db: Session):
    """
    Deletes a parking spot from the database.

    Parameters:
        spot_id (int): The unique identifier of the parking spot to be deleted.
        db (Session): The database session used to interact with the database.

    Raises:
        HTTPException (404): If the parking spot is not found (status code 404).
        HTTPException (400): If the parking spot is not empty (status code 400).
        HTTPException (500): If there is an error during the deletion process (status code 500).

    Returns:
        None
    """
    try:
        spot = db.query(Spot).filter(Spot.spot_id == spot_id).one()
        if (not spot or spot == None):
            raise HTTPException(status_code=404, detail="Spot not found.")
        if (spot.available_slots > 0):
            raise HTTPException(status_code=400, detail="Spot not empty.")
        db.query(Spot).filter(Spot.spot_id == spot_id).delete()
        db.commit()
    except Exception as db_error:
        raise HTTPException(
            status_code=500, detail="Error deleting spot: " + str(db_error))
