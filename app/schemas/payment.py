from pydantic import BaseModel 

class Payment(BaseModel):
  payment_id: int
  razorpay_signature: str
  razorpay_payment_id: str
  start_time: str
  end_time: str
  total_slots: int