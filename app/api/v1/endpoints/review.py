from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.review import Review, ReviewCreate, ReviewUpdate
from app.services.review_service import get_review, get_reviews_by_spot, create_review, update_review, delete_review
from app.db.session import get_db
from sqlalchemy.exc import IntegrityError, DataError, SQLAlchemyError

router = APIRouter()


@router.get("/{review_id}", response_model=Review)
def read_review(review_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a review by its ID.

    Parameters:
        review_id (int): The ID of the review to retrieve.
        db (Session): The database session.

    Returns:
        Review: The retrieved review.

    Raises:
        HTTPException:
            404: If the review is not found (KeyError)
            500: If an internal server error occurs or a database error occurs
    """
    try:
        db_review = get_review(db, review_id)
        return db_review
    except KeyError:
        raise HTTPException(status_code=404, detail="Review not found")
    except SQLAlchemyError as db_error:
        raise HTTPException(status_code=500, detail="DB Error: " + str(db_error))
    except Exception as general_error:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(general_error)}")



@router.get("/spot/{spot_id}", response_model=List[Review])
def read_reviews_by_spot(spot_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all reviews for a specific spot.

    Parameters:
        spot_id (int): The ID of the spot to retrieve reviews for.
        db (Session): The database session.

    Returns:
        List[Review]: A list of reviews for the specified spot.
    Raises:
        HTTPException:
            500: If an internal server error occurs    
    """
    try:
        return get_reviews_by_spot(db, spot_id)
    except SQLAlchemyError as db_error:
        raise HTTPException(status_code=500, detail="DB Error: " + str(db_error))
    except Exception as general_error:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(general_error)}")


@router.post("/", response_model=Review)
def create_new_review(review: ReviewCreate, db: Session = Depends(get_db)):
    """
    Create a new review.

    Parameters:
        review (ReviewCreate): The review data to create.
        db (Session): The database session.

    Returns:
        Review: The created review.
    Raises:
        HTTPException:
            404: If the review is not found (KeyError)
            500: If an internal server error occurs, if there is an integrity error or there is a database error
    """
    try:
        return create_review(db, review)
    except IntegrityError as integrity_error:
        raise HTTPException(status_code=500, detail="Integrity Error: " + str(integrity_error))
    except SQLAlchemyError as db_error:
        raise HTTPException(status_code=500, detail="DB Error: " + str(db_error))
    except Exception as general_error:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(general_error))

@router.put("/{review_id}", response_model=Review)
def update_existing_review(review_id: int, review: ReviewUpdate, db: Session = Depends(get_db)):
    """
    Update an existing review.

    Parameters:
        review_id (int): The ID of the review to update.
        review (ReviewUpdate): The updated review data.
        db (Session): The database session.

    Returns:
        Review: The updated review.

    Raises:
        HTTPException:
            404: If the review is not found (KeyError)
            500: If an internal server error occurs, there is a database error, or an integrity error
    """
    try:
        db_review = update_review(db, review_id, review)
        return db_review
    except KeyError:
        raise HTTPException(status_code=404, detail="Review not found")
    except IntegrityError as integrity_error:
        raise HTTPException(status_code=500, detail="Integrity Error: " + str(integrity_error))
    except SQLAlchemyError as db_error:
        raise HTTPException(status_code=500, detail="DB Error: " + str(db_error))
    except Exception as general_error:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(general_error))

@router.delete("/{review_id}", response_model=bool)
def delete_existing_review(review_id: int, db: Session = Depends(get_db)):
    """
    Delete a review by its ID.

    Parameters:
        review_id (int): The ID of the review to delete.
        db (Session): The database session.

    Returns:
        bool: True if the review was deleted, False otherwise.

    Raises:
        HTTPException:
            404: If the review is not found (KeyError)
            500: If an internal server error occurs, or there is a database error
    """
    try:
        success = delete_review(db, review_id)
        return success
    except KeyError:
        raise HTTPException(status_code=404, detail="Review not found")
    except SQLAlchemyError as db_error:
        raise HTTPException(status_code=500, detail="DB Error: " + str(db_error))
    except Exception as general_error:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(general_error))
