from fastapi import APIRouter, HTTPException
from typing import List
from decimal import Decimal
from datetime import date, timedelta
from model import Booking, BookingCreate, BookingCancel
from database import BookingDB
from database.models import BranchDB, VehicleDB

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
    # Validate that the branch exists
    branch = BranchDB.get_by_id(booking_data.branch_id)
    if not branch:
        raise HTTPException(status_code=400, detail=f"Branch with ID {booking_data.branch_id} does not exist")
    
    # Validate date range
    if booking_data.start_date > booking_data.end_date:
        raise HTTPException(status_code=400, detail="Start date must be before or equal to end date")
    
    if booking_data.start_date < date.today():
        raise HTTPException(status_code=400, detail="Start date cannot be in the past")
    
    # Check if vehicles are available for the requested category, dates, and branch
    available_vehicles = VehicleDB.get_available_vehicles(
        booking_data.category, 
        booking_data.start_date, 
        booking_data.end_date,
        booking_data.branch_id
    )
    
    if not available_vehicles:
        rental_days = (booking_data.end_date - booking_data.start_date).days + 1
        raise HTTPException(
            status_code=400, 
            detail=f"No vehicles of category '{booking_data.category}' available at branch {booking_data.branch_id} for {rental_days} days from {booking_data.start_date} to {booking_data.end_date}"
        )
    
    # Select the first available vehicle
    selected_vehicle = available_vehicles[0]
    
    # Calculate cost
    daily_rate = selected_vehicle.daily_rental_rate
    rental_days = (booking_data.end_date - booking_data.start_date).days + 1
    cost = daily_rate * rental_days
    
    # Create the booking
    booking = Booking(
        booking_id=0,  # Will be set by database
        vehicle_id=selected_vehicle.id,
        start_date=booking_data.start_date,
        end_date=booking_data.end_date,
        customer_name=booking_data.customer_name,
        cost=cost,
        branch_id=booking_data.branch_id
    )
    
    return BookingDB.create(booking)


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

    
