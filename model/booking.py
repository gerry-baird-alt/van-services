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
    branch_id: int
    
    @field_serializer('cost')
    def serialize_decimal(self, value: Decimal) -> float:
        return float(value)


class BookingCreate(BaseModel):
    model_config = ConfigDict()
    
    category: str
    start_date: date
    end_date: date
    customer_name: str
    branch_id: int


class BookingCancel(BaseModel):
    model_config = ConfigDict()
    
    booking_id: int
    start_date: date
    customer_name: str


