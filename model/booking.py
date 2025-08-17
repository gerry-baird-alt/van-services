from pydantic import BaseModel, ConfigDict, field_serializer
from decimal import Decimal
from datetime import date


class Booking(BaseModel):
    model_config = ConfigDict()
    
    booking_id: int
    vehicle_id: int
    start_date: date
    end_date: date
    customer_name: str
    cost: Decimal
    
    @field_serializer('cost')
    def serialize_decimal(self, value: Decimal) -> float:
        return float(value)


class BookingCreate(BaseModel):
    model_config = ConfigDict()
    
    category: str
    start_date: date
    duration: int  # number of days
    customer_name: str


class BookingCancel(BaseModel):
    model_config = ConfigDict()
    
    booking_id: int
    start_date: date
    customer_name: str