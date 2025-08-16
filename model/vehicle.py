from pydantic import BaseModel, ConfigDict, field_serializer
from decimal import Decimal


class Vehicle(BaseModel):
    model_config = ConfigDict()
    
    id: int
    category: str
    manufacturer: str
    model: str
    daily_rental_rate: Decimal
    number_of_seats: int
    
    @field_serializer('daily_rental_rate')
    def serialize_decimal(self, value: Decimal) -> float:
        return float(value)


class VehicleCreate(BaseModel):
    model_config = ConfigDict()
    
    category: str
    manufacturer: str
    model: str
    daily_rental_rate: Decimal
    number_of_seats: int
    
    @field_serializer('daily_rental_rate')
    def serialize_decimal(self, value: Decimal) -> float:
        return float(value)