from fastapi import APIRouter
from typing import List
from datetime import date
from model import Schedule, VehicleSearchRequest, VehicleSearchResult, Booking
from database import ScheduleDB, BookingDB

router = APIRouter(prefix="/schedule", tags=["schedules"])


@router.get("", response_model=List[Schedule])
async def get_schedule():
    return ScheduleDB.get_all()


@router.get("/vehicle/{vehicle_id}", response_model=List[Schedule])
async def get_vehicle_schedule(vehicle_id: int):
    return ScheduleDB.get_by_vehicle(vehicle_id)


@router.post("/search", response_model=List[VehicleSearchResult])
async def search_available_vehicles(search_request: VehicleSearchRequest):
    return ScheduleDB.search_available_vehicles(
        search_request.category,
        search_request.start_date,
        search_request.duration
    )
