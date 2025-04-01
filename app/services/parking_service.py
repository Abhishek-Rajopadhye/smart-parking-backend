
from sqlalchemy.orm import Session
from app.db.spot_model import Spot
from typing import List


def get_all_parking_spots(db: Session) -> List[Spot]:
    return db.query(Spot).all()
