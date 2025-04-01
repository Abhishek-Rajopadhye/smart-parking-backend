#app/schemas/user.py

from pydantic import BaseModel, EmailStr
from typing import Optional

class UserProfile(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    profile_picture: Optional[str] = None
    total_earnings: int

class UserUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    profile_picture: Optional[str] = None
    total_earnings: int
