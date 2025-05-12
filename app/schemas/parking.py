from typing import List, Optional
from pydantic import BaseModel, ConfigDict


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
    available_days: List[str]
    image: Optional[List[str]] = None
    status:int

    model_config = ConfigDict(from_attributes=True)
