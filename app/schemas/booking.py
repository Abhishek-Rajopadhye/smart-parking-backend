from pydantic import BaseModel


class BookingCreate(BaseModel):
    user_id: str
    spot_id: int
    total_slots: int
    start_date_time: str
    end_date_time: str
    total_amount: int
    receipt: str
