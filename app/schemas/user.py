# app/schemas/user.py

from pydantic import BaseModel, EmailStr
from typing import Optional


class UserProfile(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    profile_picture: Optional[str] = None
    total_earnings: int


class OwnerProfile(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    profile_picture: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    profile_picture: Optional[str] = None
    total_earnings: Optional[int] = None
