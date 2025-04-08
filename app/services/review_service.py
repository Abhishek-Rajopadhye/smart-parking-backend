from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewInDB
from app.db.review_model import Review


def get_review(db: Session, review_id: int) -> Optional[ReviewInDB]:
    """
    Retrieve a review by its ID.

    Parameters:
        db (Session): The database session.
        review_id (int): The ID of the review to retrieve.

    Returns:
        Optional[ReviewInDB]: The retrieved review, or None if not found.
    """
    return db.query(Review).filter(Review.id == review_id).first()


def get_reviews_by_spot(db: Session, spot_id: int) -> List[ReviewInDB]:
    """
    Retrieve all reviews for a specific spot.

    Parameters:
        db (Session): The database session.
        spot_id (int): The ID of the spot to retrieve reviews for.

    Returns:
        List[ReviewInDB]: A list of reviews for the specified spot.
    """
    reviews = db.query(Review).filter(
        Review.spot_id == spot_id).options(joinedload(Review.user)).all()
    return [
        ReviewInDB(
            id=r.id,
            created_at=r.created_at,
            user_id=r.user_id,
            reviewer_name=r.user.name if r.user else "Unknown",  # Get user's name
            spot_id=r.spot_id,
            rating_score=r.rating_score,
            review_description=r.review_description,
            image=r.image,
            owner_reply=r.owner_reply
        )
        for r in reviews
    ]


def create_review(db: Session, review: ReviewCreate) -> ReviewInDB:
    """
    Create a new review.

    Parameters:
        db (Session): The database session.
        review (ReviewCreate): The review data to create.

    Returns:
        ReviewInDB: The created review.
    """
    db_review = Review(**review.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


def update_review(db: Session, review_id: int, review: ReviewUpdate) -> Optional[ReviewInDB]:
    """
    Update an existing review.

    Parameters:
        db (Session): The database session.
        review_id (int): The ID of the review to update.
        review (ReviewUpdate): The updated review data.

    Returns:
        Optional[ReviewInDB]: The updated review, or None if not found.
    """
    db_review = db.query(Review).filter(Review.id == review_id).first()
    if db_review is None:
        return None

    for key, value in review.dict(exclude_unset=True).items():
        setattr(db_review, key, value)

    db.commit()
    db.refresh(db_review)
    return db_review


def delete_review(db: Session, review_id: int) -> bool:
    """
    Delete a review by its ID.

    Parameters:
        db (Session): The database session.
        review_id (int): The ID of the review to delete.

    Returns:
        bool: True if the review was deleted, False otherwise.
    """
    db_review = db.query(Review).filter(Review.id == review_id).first()
    if db_review is None:
        return False

    db.delete(db_review)
    db.commit()
    return True
