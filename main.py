from fastapi import FastAPI, HTTPException
from typing import Optional
from decimal import Decimal
from datetime import date, timedelta
from contextlib import asynccontextmanager
from model import Vehicle, VehicleCreate, Booking, BookingCreate, Schedule, VehicleSearchRequest, VehicleSearchResult
from database import init_db, insert_sample_data, VehicleDB, BookingDB, ScheduleDB


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    insert_sample_data()
    yield
    # Shutdown (if needed)


app = FastAPI(lifespan=lifespan)


@app.get("/vehicle", response_model=list[Vehicle])
async def get_vehicles():
    return VehicleDB.get_all()


@app.get("/vehicle/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(vehicle_id: int):
    vehicle = VehicleDB.get_by_id(vehicle_id)
    if vehicle:
        return vehicle
    raise HTTPException(status_code=404, detail="Vehicle not found")


@app.post("/vehicle", response_model=Vehicle)
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


@app.get("/booking", response_model=list[Booking])
async def get_bookings():
    return BookingDB.get_all()


@app.get("/booking/{booking_id}", response_model=Booking)
async def get_booking(booking_id: int):
    booking = BookingDB.get_by_id(booking_id)
    if booking:
        return booking
    raise HTTPException(status_code=404, detail="Booking not found")


@app.post("/booking", response_model=Booking)
async def create_booking(booking_data: BookingCreate):
    # Check if vehicles are available for the requested category and dates
    available_vehicles = ScheduleDB.search_available_vehicles(
        booking_data.category, 
        booking_data.start_date, 
        booking_data.duration
    )
    
    if not available_vehicles:
        raise HTTPException(
            status_code=400, 
            detail=f"No vehicles of category '{booking_data.category}' available for {booking_data.duration} days starting {booking_data.start_date}"
        )
    
    # Select the first available vehicle
    selected_vehicle = available_vehicles[0]
    
    # Calculate end date and cost
    end_date = booking_data.start_date + timedelta(days=booking_data.duration - 1)
    cost = Decimal(str(selected_vehicle.total_cost))
    
    # Create the booking
    booking = Booking(
        booking_id=0,  # Will be set by database
        vehicle_id=selected_vehicle.vehicle_id,
        start_date=booking_data.start_date,
        end_date=end_date,
        customer_name=booking_data.customer_name,
        cost=cost
    )
    
    created_booking = BookingDB.create(booking)
    
    # Update schedule entries for the booked dates
    for day in range(booking_data.duration):
        schedule_date = booking_data.start_date + timedelta(days=day)
        schedule_entry = Schedule(
            date=schedule_date,
            vehicle_id=selected_vehicle.vehicle_id,
            status="booked",
            booking_id=created_booking.booking_id
        )
        ScheduleDB.create(schedule_entry)
    
    return created_booking


@app.get("/schedule", response_model=list[Schedule])
async def get_schedule():
    return ScheduleDB.get_all()


@app.get("/schedule/vehicle/{vehicle_id}", response_model=list[Schedule])
async def get_vehicle_schedule(vehicle_id: int):
    return ScheduleDB.get_by_vehicle(vehicle_id)


@app.post("/schedule/search", response_model=list[VehicleSearchResult])
async def search_available_vehicles(search_request: VehicleSearchRequest):
    return ScheduleDB.search_available_vehicles(
        search_request.category,
        search_request.start_date,
        search_request.duration
    )
