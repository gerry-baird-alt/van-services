from pydantic import BaseModel
from datetime import date


class VehicleSearchRequest(BaseModel):
    category: str
    start_date: date
    duration: int  # number of days


class VehicleSearchResult(BaseModel):
    vehicle_id: int
    category: str
    manufacturer: str
    model: str
    daily_rental_rate: float
    number_of_seats: int
    total_cost: float