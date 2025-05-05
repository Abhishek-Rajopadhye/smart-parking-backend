from pydantic import BaseModel
from typing import Optional
from fastapi import UploadFile


class AddSpot(BaseModel):
    spot_address: str
    owner_id: str
    spot_title: str
    latitude: float
    longitude: float
    available_slots: int
    total_slots: int
    hourly_rate: int
    open_time: str
    close_time: str
    verification_status:int
    spot_description: Optional[str] = None
    available_days: list[str] = None
    image: Optional[list[str]] = None
    doc1: UploadFile = None
    doc2: UploadFile = None
    doc3: UploadFile = None

class EditSpot(BaseModel):
    spot_address: str
    spot_title: str
    total_slots: int
    hourly_rate: int
    open_time: str
    close_time: str
    spot_description: Optional[str] = None
    available_days: list[str] = None
    image: Optional[list[str]] = None
