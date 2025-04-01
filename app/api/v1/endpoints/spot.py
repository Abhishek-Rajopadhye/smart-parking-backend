from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session #interact with database
from app.db.session import get_db
from app.services.spot_service import add_spot
from app.schemas.spot import AddSpot

router = APIRouter()

@router.post("/add-spot")
def add_spot_route(spot_data: AddSpot, db: Session = Depends(get_db)):
    """
    Add a parking spot for the user.

    Args:
        spot_data (AddSpot): Spot data
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        dict: Response message otherwise raise appropriate HTTPException and return the error message

    Example:
        add_spot_route(spot_data)
        add a parking spot for the user
        return the spot details
    """
    try:
        print("Hi")
        response = add_spot(spot_data, db)
        print(response)
        if "error" in response:
            raise HTTPException(status_code=400, detail=response["detail"])
        return response
    except Exception as exception:
        print(exception)
        raise HTTPException(status_code=400, detail=exception.detail)