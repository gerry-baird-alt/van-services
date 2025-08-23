from fastapi import APIRouter, HTTPException
from typing import List
from decimal import Decimal
from datetime import date, timedelta
from model import Booking, BookingCreate, BookingCancel, Schedule, BookingWithVehicle
from database import BookingDB, ScheduleDB

router = APIRouter(prefix="/booking", tags=["bookings"])


@router.get("", response_model=List[Booking])
async def get_bookings():
    return BookingDB.get_all()


@router.get("/{booking_id}", response_model=Booking)
async def get_booking(booking_id: int):
    booking = BookingDB.get_by_id(booking_id)
    if booking:
        return booking
    raise HTTPException(status_code=404, detail="Booking not found")


@router.post("", response_model=Booking)
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


@router.post("/cancel")
async def cancel_booking(cancel_data: BookingCancel):
    """Cancel a booking by booking_id, start_date, and customer_name."""
    success = BookingDB.delete(
        cancel_data.booking_id,
        cancel_data.start_date,
        cancel_data.customer_name
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Booking not found or invalid credentials"
        )
    
    return {"message": "Booking cancelled successfully"}

    
@router.get("/by_date/{target_date}", response_model=List[Booking])
async def get_bookings_for_date(target_date: date):
    """Get all bookings that are active on a specific date."""
    return BookingDB.get_by_date(target_date)


@router.get("/by_date_with_vehicle/{target_date}", response_model=List[BookingWithVehicle])
async def get_bookings_for_date_with_vehicle(target_date: date):
    """Get all bookings that are active on a specific date with vehicle details."""
    return BookingDB.get_by_date_with_vehicle(target_date)