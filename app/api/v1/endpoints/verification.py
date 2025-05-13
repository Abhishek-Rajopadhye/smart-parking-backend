from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.verification import SpotVerification
from app.services.verification_service import get_pending_spot_verifications, accept_request, reject_request
import base64

def spot_to_dict(spot):
    import base64
    result = {column.name: getattr(spot, column.name) for column in spot.__table__.columns}
    # Handle image field
    if "image" in result:
        if isinstance(result["image"], bytes):
            result["image"] = base64.b64encode(result["image"]).decode("utf-8")
        elif isinstance(result["image"], list):
            # Encode each image in the list if not empty
            result["image"] = [
                base64.b64encode(img).decode("utf-8") if isinstance(img, bytes) else img
                for img in result["image"]
            ] if result["image"] else []
        # If None, leave as is
    return result

router = APIRouter()


@router.get("/", response_model=List[SpotVerification])
def get_validation_requests_list(db: Session = Depends(get_db)):
    """
    Retrieve a list of all spots pending verification (validation_status == 0), 
    along with their associated documents sorted by document type.

    Parameters:
        db (Session): The database session

    Returns:
        List[SpotVerification]: List of spots with their documents for verification

    Raises:
        HTTPException:
            404: If no pending spots are found (KeyError)
            400: If the request is malformed (ValueError, TypeError)
            500: Any other error occurs during the process (Exceptione)
    """
    try:
        return_list = get_pending_spot_verifications(db)
        if not return_list:
            raise HTTPException(
                status_code=404, detail="No pending verification requests found.")
        return return_list
    except HTTPException as http_exc:
        raise http_exc
    except KeyError as no_pending_spots:
        raise HTTPException(status_code=404, detail=str(no_pending_spots))
    except ValueError as value_error:
        raise HTTPException(
            status_code=400, detail=f"Bad request: {str(value_error)}")
    except TypeError as type_error:
        raise HTTPException(
            status_code=400, detail=f"Type error: {str(type_error)}")
    except Exception as general_error:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(general_error)}")


@router.put("/request/accept/{spot_id}")
def accept_verification_request(spot_id: int, db: Session = Depends(get_db)):
    """
    Accept a spot verification request by updating the spot's validation_status to 1.

    Parameters:
        spot_id (int): The ID of the spot to accept
        db (Session): The database session

    Returns:
        Spot: The updated spot object


    Raises:
        HTTPException:
            404: If the spot is not found (KeyError)
            400: If the request is malformed (ValueError, TypeError)
            500: Any other error occurs during the process (Exception)
    """
    try:
        return_spot = accept_request(db, spot_id)
        return spot_to_dict(return_spot)
    except KeyError as spot_not_found:
        raise HTTPException(status_code=404, detail=str(spot_not_found))
    except ValueError as value_error:
        raise HTTPException(
            status_code=400, detail=f"Bad request: {str(value_error)}")
    except TypeError as type_error:
        raise HTTPException(
            status_code=400, detail=f"Type error: {str(type_error)}")
    except Exception as general_error:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(general_error)}")


@router.put("/request/reject/{spot_id}")
def reject_verification_request(spot_id: int, db: Session = Depends(get_db)):
    """
    Reject a spot verification request by updating the spot's validation_status to -1.

    Parameters:
        spot_id (int): The ID of the spot to reject
        db (Session): The database session

    Returns:
        Spot: The updated spot object

    Raises:
        HTTPException:
            404: If the spot is not found (KeyError)
            400: If the request is malformed (ValueError, TypeError)
            500: Any other error occurs during the process (Exception)
    """
    try:
        return_spot = reject_request(db, spot_id)
        return spot_to_dict(return_spot)
    except KeyError as spot_not_found:
        raise HTTPException(status_code=404, detail=str(spot_not_found))
    except ValueError as value_error:
        raise HTTPException(
            status_code=400, detail=f"Bad request: {str(value_error)}")
    except TypeError as type_error:
        raise HTTPException(
            status_code=400, detail=f"Type error: {str(type_error)}")
    except Exception as general_error:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(general_error)}")
