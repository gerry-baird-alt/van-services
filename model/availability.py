from pydantic import BaseModel, ConfigDict, field_serializer
from decimal import Decimal
from datetime import date
from typing import Optional


class AvailabilityRequest(BaseModel):
    model_config = ConfigDict()
    
    start_date: date
    end_date: date
    category: Optional[str] = None
    branch_id: Optional[int] = None


class AvailableVehicle(BaseModel):
    model_config = ConfigDict()
    
    vehicle_id: int
    category: str
    manufacturer: str
    model: str
    daily_rental_rate: Decimal
    number_of_seats: int
    branch_id: int
    total_cost: Decimal
    
    @field_serializer('daily_rental_rate', 'total_cost')
    def serialize_decimal(self, value: Decimal) -> float:
        return float(value)