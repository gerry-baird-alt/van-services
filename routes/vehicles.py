from fastapi import APIRouter, HTTPException
from typing import List
from model import Vehicle, VehicleCreate
from database import VehicleDB

router = APIRouter(prefix="/vehicle", tags=["vehicles"])


@router.get("", response_model=List[Vehicle])
async def get_vehicles():
    return VehicleDB.get_all()


@router.get("/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(vehicle_id: int):
    vehicle = VehicleDB.get_by_id(vehicle_id)
    if vehicle:
        return vehicle
    raise HTTPException(status_code=404, detail="Vehicle not found")


@router.post("", response_model=Vehicle)
async def create_vehicle(vehicle_data: VehicleCreate):
    vehicle = Vehicle(
        id=0,  # Will be set by database
        category=vehicle_data.category,
        manufacturer=vehicle_data.manufacturer,
        model=vehicle_data.model,
        daily_rental_rate=vehicle_data.daily_rental_rate,
        number_of_seats=vehicle_data.number_of_seats
    )
    return VehicleDB.create(vehicle)