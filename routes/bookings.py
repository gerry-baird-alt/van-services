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
    """
    Get all bookings in the system.
    
    Returns a complete list of all customer reservations including:
    - Booking details (ID, dates, customer name)
    - Assigned vehicle information
    - Total cost and branch location
    - Current booking status
    
    Returns:
        List of all Booking objects with complete reservation details
    """
    return BookingDB.get_all()


@router.get("/{booking_id}", response_model=Booking)
async def get_booking(booking_id: int):
    """
    Get a specific booking by its ID.
    
    Retrieves detailed information for a single customer reservation including
    all booking details, assigned vehicle, and cost information.
    
    Args:
        booking_id: The unique identifier of the booking
        
    Returns:
        Booking object with complete reservation details including:
            - Customer information and dates
            - Assigned vehicle details
            - Total cost and branch location
            
    Raises:
        HTTPException: 404 if booking with the specified ID is not found
    """
    booking = BookingDB.get_by_id(booking_id)
    if booking:
        return booking
    raise HTTPException(status_code=404, detail="Booking not found")


@router.post("", response_model=Booking)
async def create_booking(booking_data: BookingCreate):
    """
    Create a new vehicle booking reservation.
    
    This endpoint handles the complete booking process including:
    - Validation of branch existence and date ranges
    - Vehicle availability checking for requested category/dates/branch
    - Automatic vehicle selection and cost calculation
    - Booking creation with assigned vehicle
    
    The system automatically selects the first available vehicle matching the criteria
    and calculates the total cost based on daily rates and rental duration.
    
    Args:
        booking_data: BookingCreate containing:
            - category: Requested vehicle size (Small, Medium, Large)
            - start_date: Rental start date (cannot be in past)
            - end_date: Rental end date (must be >= start_date)
            - customer_name: Name for the reservation
            - branch_id: Branch location for pickup/return
            
    Returns:
        Complete Booking object with:
            - Assigned booking ID and vehicle
            - Confirmed dates and customer details
            - Calculated total cost
            - Branch location information
            
    Raises:
        HTTPException:
            - 400 if branch doesn't exist
            - 400 if date range is invalid or in past
            - 400 if no vehicles available for requested criteria
    """
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
    """
    Cancel an existing booking reservation.
    
    This endpoint provides secure booking cancellation by requiring multiple
    verification fields to prevent unauthorized cancellations. All three
    fields must match exactly for the cancellation to proceed.
    
    Args:
        cancel_data: BookingCancel containing:
            - booking_id: The unique booking identifier
            - start_date: The original booking start date
            - customer_name: The name on the reservation
            
    Returns:
        Success confirmation message when booking is cancelled
        
    Raises:
        HTTPException: 404 if booking not found or credentials don't match exactly
        
    Security Note:
        Requires exact match of booking ID, start date, and customer name
        to prevent unauthorized booking modifications.
    """
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

    
