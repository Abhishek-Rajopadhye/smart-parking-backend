from sqlalchemy  import text
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session  # interact with database
from app.db.session import get_db
from app.services.parking_service import get_all_parking_spots
from app.schemas.parking import ParkingSpot
from typing import List
import base64

router = APIRouter()

@router.get("/getparkingspot", response_model=List[ParkingSpot])
async def fetch_parking_spots(db: Session = Depends(get_db)):
    """
    Fetch  list of all  parking spots.

    This endpoint connects to the database, fetches all parking spot records
    using the `get_all_parking_spots` service, and returns them as a list
    of `ParkingSpot` objects.

    Parameters:
        db (Session): The database session .

    Returns:
        List[ParkingSpot]: List  containing details of all parking spots.
    """
    try:
        spots = get_all_parking_spots(db)
        for spot in spots:
            if spot.image:  # Assuming `image` is a binary field
                spot.image = base64.b64encode(spot.image).decode("utf-8")
        return spots
    except Exception as error:
        raise HTTPException(status_code=500,details=f"Could not get parking spots detail : {error}")
    
    
@router.get("/get-image/{spot_id}")
def get_parking_spots(spot_id: int, db: Session = Depends(get_db)):
    query = text("SELECT image FROM spots WHERE spot_id = :spot_id")
    result = db.execute(query, {"spot_id": spot_id}).fetchone()  # Fetch first row

    if not result:
        raise HTTPException(status_code=404, detail=f"Spot ID {spot_id} not found.")

    image_bytes = result[0]  # Extract image column from the tuple
    print(image_bytes)
    if not image_bytes:
        raise HTTPException(status_code=404, detail=f"Image for Spot ID {spot_id} is missing.")

    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    return {"image": image_base64}