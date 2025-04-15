from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session  # interact with database
from app.db.session import get_db
from app.services.spot_service import add_spot, get_spot_list_of_owner, update_spot_details, delete_spot
from app.schemas.spot import AddSpot, EditSpot

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


@router.get("/owner/{user_id}")
def get_spots_of_owner(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all spots owned by a specific user.

    Args:
        user_id (int): User ID
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        List[dict]: List of spots for the specified user
    """
    return get_spot_list_of_owner(user_id, db)


@router.put("/{spot_id}")
async def update_spot(spot_id: int, updated_spot: EditSpot, db: Session = Depends(get_db)):
    """
    Update the details of a parking spot.

    Args:
        spot_id (int): The unique identifier of the parking spot to be updated.
        updated_spot (EditSpot): An object containing the updated details of the parking spot.
        db (Session): The database session dependency.

    Returns:
        dict: The updated parking spot details after applying the changes.
    """
    return await update_spot_details(updated_spot, spot_id, db)


@router.delete("/{spot_id}")
def delete_selected_spot(spot_id: int, db: Session = Depends(get_db)):
    """
    Deletes a parking spot with the specified ID.

    Args:
        spot_id (int): The ID of the parking spot to be deleted.
        db (Session, optional): The database session dependency. Defaults to the result of `Depends(get_db)`.

    Returns:
        None: The result of the `delete_spot` function, which handles the deletion logic.
    """
    return delete_spot(spot_id, db)
