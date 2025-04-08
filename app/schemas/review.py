from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReviewBase(BaseModel):
    user_id: str
    spot_id: int
    rating_score: int = Field(..., ge=1, le=5,
                              description="Rating score must be between 1 and 5")
    review_description: Optional[str] = None
    images: Optional[list[bytes]] = None
    owner_reply: Optional[str] = None


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(ReviewBase):
    pass


class ReviewInDBBase(ReviewBase):
    id: int
    created_at: datetime
    reviewer_name: Optional[str] = None

    class Config:
        orm_mode: True


class Review(ReviewInDBBase):
    pass


class ReviewInDB(ReviewInDBBase):
    pass
