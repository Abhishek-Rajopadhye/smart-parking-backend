from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.spot_model import Spot, Document
from typing import List, Optional
from app.schemas.verification import SpotVerification, DocumentInfo


def get_pending_spot_verifications(db: Session) -> List[SpotVerification]:
    """
    Retrieve a list of all spots pending verification (verification_status == 0), 
    along with their associated documents sorted by document type.

    Parameters:
        db (Session): The database session

    Returns:
        List[SpotVerification]: List of spots with their documents for verification

    Raises:
        KeyError: If no pending verification requests are found.
        ValueError: If there is a value error during processing.
        TypeError: If there is a type error during processing.
        Exception: For any other unexpected errors.
    """
    try:
        spots = db.query(Spot).filter(Spot.verification_status == 0).all()
        if not spots:
            raise KeyError("No pending verification requests found.")

        pending_spots = []
        for spot in spots:
            documents = db.query(Document).filter(
                Document.spot_id == spot.spot_id).all()
            identity_proof_document: Optional[DocumentInfo] = None
            ownership_proof_document: Optional[DocumentInfo] = None
            supporting_document: Optional[DocumentInfo] = None

            for doc in documents:
                doc_info = DocumentInfo(
                    file_name=doc.filename,
                    file_type=doc.document_type,
                    file_data=doc.content,
                    uploaded_at=doc.uploaded_at
                )
                if doc.document_type.lower() == "identity_proof":
                    identity_proof_document = doc_info
                elif doc.document_type.lower() == "ownership_proof":
                    ownership_proof_document = doc_info
                elif doc.document_type.lower() == "supporting_document":
                    supporting_document = doc_info

            pending_spots.append(
                SpotVerification(
                    spot_id=spot.spot_id,
                    spot_title=spot.spot_title,
                    spot_description=getattr(spot, "description", ""),
                    spot_address=getattr(spot, "address", ""),
                    owner_id=spot.owner_id,
                    identity_proof_document=identity_proof_document,
                    ownership_proof_document=ownership_proof_document,
                    supporting_document=supporting_document
                )
            )
        return pending_spots
    except KeyError as no_pending_spots:
        raise no_pending_spots
    except ValueError as value_error:
        raise value_error
    except TypeError as type_error:
        raise type_error
    except Exception as general_error:
        raise general_error


def accept_request(db: Session, spot_id: int):
    """
    Accept a spot verification request by updating the spot's verification_status to 1.

    Parameters:
        db (Session): The database session
        spot_id (int): The ID of the spot to accept

    Returns:
        Spot: The updated spot object

    Raises:
        KeyError: If the spot is not found.
        ValueError: If there is a value error during processing.
        TypeError: If there is a type error during processing.
        Exception: For any other unexpected errors.
    """
    try:
        spot_check = db.query(Spot.spot_id).filter(Spot.spot_id == spot_id).first()
        if not spot_check:
            raise KeyError("Spot not found")
        spot = db.query(Spot).filter(Spot.spot_id == spot_id).first()
        spot.verification_status = 1
        db.commit()
        db.refresh(spot)
        return spot
    except KeyError as spot_not_found:
        raise spot_not_found
    except ValueError as value_error:
        raise value_error
    except TypeError as type_error:
        raise type_error
    except Exception as general_error:
        raise general_error


def reject_request(db: Session, spot_id: int):
    """
    Reject a spot verification request by updating the spot's verification_status to -1.

    Parameters:
        db (Session): The database session
        spot_id (int): The ID of the spot to reject

    Returns:
        Spot: The updated spot object

    Raises:
        KeyError: If the spot is not found.
        ValueError: If there is a value error during processing.
        TypeError: If there is a type error during processing.
        Exception: For any other unexpected errors.
    """
    try:
        spot_check = db.query(Spot.spot_id).filter(Spot.spot_id == spot_id).first()
        if not spot_check:
            raise KeyError("Spot not found")
        spot = db.query(Spot).filter(Spot.spot_id == spot_id).first()
        spot.verification_status = -1
        db.commit()
        db.refresh(spot)
        return spot
    except KeyError as spot_not_found:
        raise spot_not_found
    except ValueError as value_error:
        raise value_error
    except TypeError as type_error:
        raise type_error
    except Exception as general_error:
        raise general_error
