from typing import List, Optional
from pydantic import BaseModel

class ParkingSpot(BaseModel):
    spot_id: int
    address: str
    owner_id: str
    spot_title: str
    latitude: float
    longitude: float
    available_slots: int
    no_of_slots: int
    hourly_rate: int
    open_time: str
    close_time: str
    description: Optional[str] = None
    available_days: list[str]
    image: str
