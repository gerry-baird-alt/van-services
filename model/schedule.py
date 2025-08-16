from pydantic import BaseModel
from datetime import date
from typing import Optional


class Schedule(BaseModel):
    date: date
    vehicle_id: int
    status: str
    booking_id: Optional[int] = None