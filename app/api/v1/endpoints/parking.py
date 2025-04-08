from sqlalchemy import text
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
    try:
        spots = get_all_parking_spots(db)
        out: List[dict] = []

        for s in spots:
            # Manually assemble a dict matching your Pydantic schema:
            spot_dict = {
                "spot_id":         s.spot_id,
                "address":         s.address,
                "owner_id":        s.owner_id,
                "spot_title":      s.spot_title,
                "latitude":        s.latitude,
                "longitude":       s.longitude,
                "available_slots": s.available_slots,
                "no_of_slots":     s.no_of_slots,
                "hourly_rate":     s.hourly_rate,
                "open_time":       s.open_time,
                "close_time":      s.close_time,
                "description":     s.description,
                "available_days":  s.available_days,
                # **Convert each bytes blob to a base64 string:**
                "image": [
                    base64.b64encode(blob).decode("utf-8")
                    for blob in (s.image or [])
                ],
            }
            out.append(spot_dict)

        return out

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Could not get parking spots detail: {error}"
        )


@router.get("/get-images/{spot_id}")
def get_images(spot_id: int, db: Session = Depends(get_db)):
    """
    Fetch ALL image blobs for a given spot_id,
    encode each as base64, and return as JSON array.
    """
    row = db.execute(
        text("SELECT image FROM spots WHERE spot_id = :spot_id"),
        {"spot_id": spot_id}
    ).fetchone()

    if not row or not row[0]:
        raise HTTPException(
            status_code=404, detail="No images found for this spot.")

    # row[0] is either bytes (single) or list[bytes]
    blobs = row[0] if isinstance(row[0], (list, tuple)) else [row[0]]

    images_b64 = [base64.b64encode(blob).decode("utf-8") for blob in blobs]

    return {"images": images_b64}
