from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.review import Review, ReviewCreate, ReviewUpdate
from app.services.review_service import get_review, get_reviews_by_spot, create_review, update_review, delete_review
from app.db.session import get_db

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
        HTTPException: If the review is not found.
    """
    db_review = get_review(db, review_id)
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return db_review


@router.get("/spot/{spot_id}", response_model=List[Review])
def read_reviews_by_spot(spot_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all reviews for a specific spot.

    Parameters:
        spot_id (int): The ID of the spot to retrieve reviews for.
        db (Session): The database session.

    Returns:
        List[Review]: A list of reviews for the specified spot.
    """
    return get_reviews_by_spot(db, spot_id)


@router.post("/", response_model=Review)
def create_new_review(review: ReviewCreate, db: Session = Depends(get_db)):
    """
    Create a new review.

    Parameters:
        review (ReviewCreate): The review data to create.
        db (Session): The database session.

    Returns:
        Review: The created review.
    """
    return create_review(db, review)


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
        HTTPException: If the review is not found.
    """
    db_review = update_review(db, review_id, review)
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return db_review


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
        HTTPException: If the review is not found.
    """
    success = delete_review(db, review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")
    return success
