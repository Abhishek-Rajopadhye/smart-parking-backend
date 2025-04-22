from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter()


@router.get("/")
def get_validation_requests_list(): # db: Session = Depends(get_db)
    try:
        return [
            {
                "spot_id": 1,
                "spot_title": "ABC",
                "spot_address": "ABC GEF",
                                "identityProof": "",
                                "ownershipProof": "",
                                "noc": "",
            },
            {
                "spot_id": 2,
                "spot_title": "XYZ",
                "spot_address": "XYZ PQR",
                                "identityProof": "",
                                "ownershipProof": "",
                                "noc": "",
            },
            {
                "spot_id": 3,
                "spot_title": "LMN",
                "spot_address": "LMN PQR",
                                "identityProof": "",
                                "ownershipProof": "",
                                "noc": "",
            }
        ]
    except Exception as general_error:
        raise HTTPException(status_code=500, detail="Error")


@router.put("/request/accept/{spot_id}")
def accept_request(spot_id: int):
    return True


@router.put("/request/reject/{spot_id}")
def accept_request(spot_id: int):
    return False
