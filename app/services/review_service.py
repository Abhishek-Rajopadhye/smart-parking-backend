from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewInDB
from app.db.review_model import Review
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

def get_review(db: Session, review_id: int) -> Optional[ReviewInDB]:
    """
    Retrieve a review by its ID.

    Parameters:
        db (Session): The database session.
        review_id (int): The ID of the review to retrieve.

    Returns:
        Optional[ReviewInDB]: The retrieved review, or None if not found.

    Raises:
        KeyError: If the review is not found.
        SQLAlchemyError: If a database error occurs.
        Exception: For any other unexpected errors.
    """
    try:
        db_review = db.query(Review).filter(Review.id == review_id).first()
        if db_review is None:
            raise KeyError("Review not found")
        return db_review
    except SQLAlchemyError as db_error:
        raise db_error
    except Exception as general_error:
        raise general_error

def get_reviews_by_spot(db: Session, spot_id: int) -> List[ReviewInDB]:
    """
    Retrieve all reviews for a specific spot.

    Parameters:
        db (Session): The database session.
        spot_id (int): The ID of the spot to retrieve reviews for.

    Returns:
        List[ReviewInDB]: A list of reviews for the specified spot.

    Raises:
        SQLAlchemyError: If a database error occurs.
        Exception: For any other unexpected errors.
    """
    try:
        reviews = db.query(Review).filter(
            Review.spot_id == spot_id).options(joinedload(Review.user)).all()
        
        return [
            ReviewInDB(
                id=review.id,
                created_at=review.created_at,
                user_id=review.user_id,
                reviewer_name=review.user.name if review.user else "Unknown",
                spot_id=review.spot_id,
                rating_score=review.rating_score,
                review_description=review.review_description,
                images=review.images,
                owner_reply=review.owner_reply
            )
            for review in reviews
        ]
    except SQLAlchemyError as db_error:
        raise db_error
    except Exception as general_error:
        raise general_error

def create_review(db: Session, review: ReviewCreate) -> ReviewInDB:
    """
    Create a new review.

    Parameters:
        db (Session): The database session.
        review (ReviewCreate): The review data to create.

    Returns:
        ReviewInDB: The created review.

    Raises:
        IntegrityError: If there is a constraint violation.
        SQLAlchemyError: If a database error occurs.
        Exception: For any other unexpected errors.
    """
    try:
        db_review = Review(**review.model_dump())
        db.add(db_review)
        db.commit()
        db.refresh(db_review)
        return db_review
    except IntegrityError as integrity_error:
        db.rollback()
        raise integrity_error
    except SQLAlchemyError as db_error:
        db.rollback()
        raise db_error
    except Exception as general_error:
        db.rollback()
        raise general_error

def update_review(db: Session, review_id: int, review: ReviewUpdate) -> Optional[ReviewInDB]:
    """
    Update an existing review.

    Parameters:
        db (Session): The database session.
        review_id (int): The ID of the review to update.
        review (ReviewUpdate): The updated review data.

    Returns:
        Optional[ReviewInDB]: The updated review, or None if not found.

    Raises:
        KeyError: If the review is not found.
        IntegrityError: If there is a constraint violation.
        SQLAlchemyError: If a database error occurs.
        Exception: For any other unexpected errors.
    """
    try:
        db_review = db.query(Review).filter(Review.id == review_id).first()
        if db_review is None:
            raise KeyError("Review not found")

        for key, value in review.dict(exclude_unset=True).items():
            setattr(db_review, key, value)

        db.commit()
        db.refresh(db_review)
        return db_review
    except IntegrityError as integrity_error:
        db.rollback()
        raise integrity_error
    except SQLAlchemyError as db_error:
        db.rollback()
        raise db_error
    except Exception as general_error:
        db.rollback()
        raise general_error

def delete_review(db: Session, review_id: int) -> bool:
    """
    Delete a review by its ID.

    Parameters:
        db (Session): The database session.
        review_id (int): The ID of the review to delete.

    Returns:
        bool: True if the review was deleted, False otherwise.

    Raises:
        KeyError: If the review is not found.
        SQLAlchemyError: If a database error occurs.
        Exception: For any other unexpected errors.
    """
    try:
        db_review = db.query(Review).filter(Review.id == review_id).first()
        if db_review is None:
            raise KeyError("Review not found")

        db.delete(db_review)
        db.commit()
        return True
    except SQLAlchemyError as db_error:
        db.rollback()
        raise db_error
    except Exception as general_error:
        db.rollback()
        raise general_error