
from sqlalchemy.orm import Session
from app.db.spot_model import Spot
from typing import List


def get_all_parking_spots(db: Session) -> List[Spot]:
    return db.query(Spot).filter(Spot.verification_status.in_([1, 3])).all()


def get_parking_spot_by_id(db: Session, spot_id: int) -> Spot:
    return db.query(Spot).filter(Spot.spot_id == spot_id).first()
