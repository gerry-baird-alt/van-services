from fastapi import APIRouter, HTTPException
from typing import List
from datetime import date, timedelta
from model import AvailabilityRequest, AvailableVehicle
from database.models import VehicleDB, BranchDB

router = APIRouter(prefix="/availability", tags=["availability"])


@router.post("/search", response_model=List[AvailableVehicle])
async def search_available_vehicles(request: AvailabilityRequest):
    """Search for available vehicles based on date range and optional filters."""
    
    # Validate date range
    if request.start_date > request.end_date:
        raise HTTPException(status_code=400, detail="Start date must be before or equal to end date")
    
    if request.start_date < date.today():
        raise HTTPException(status_code=400, detail="Start date cannot be in the past")
    
    # If branch_id is specified, validate that the branch exists
    if request.branch_id is not None:
        branch = BranchDB.get_by_id(request.branch_id)
        if not branch:
            raise HTTPException(status_code=400, detail=f"Branch with ID {request.branch_id} does not exist")
    
    # Get all vehicles that match the criteria
    if request.category and request.branch_id:
        # Filter by both category and branch
        available_vehicles = VehicleDB.get_available_vehicles(
            request.category, 
            request.start_date, 
            request.end_date, 
            request.branch_id
        )
    elif request.category:
        # Filter by category only - get vehicles from all branches
        all_vehicles = VehicleDB.get_all()
        category_vehicles = [v for v in all_vehicles if v.category == request.category]
        available_vehicles = []
        
        for vehicle in category_vehicles:
            # Check if this vehicle is available
            vehicle_available = VehicleDB.get_available_vehicles(
                vehicle.category,
                request.start_date,
                request.end_date,
                vehicle.branch_id
            )
            if any(av.id == vehicle.id for av in vehicle_available):
                available_vehicles.append(vehicle)
    
    elif request.branch_id:
        # Filter by branch only - get all categories from this branch
        all_vehicles = VehicleDB.get_all()
        branch_vehicles = [v for v in all_vehicles if v.branch_id == request.branch_id]
        available_vehicles = []
        
        for vehicle in branch_vehicles:
            # Check if this vehicle is available
            vehicle_available = VehicleDB.get_available_vehicles(
                vehicle.category,
                request.start_date,
                request.end_date,
                vehicle.branch_id
            )
            if any(av.id == vehicle.id for av in vehicle_available):
                available_vehicles.append(vehicle)
    
    else:
        # No filters - get all available vehicles from all branches and categories
        all_vehicles = VehicleDB.get_all()
        available_vehicles = []
        
        for vehicle in all_vehicles:
            # Check if this vehicle is available
            vehicle_available = VehicleDB.get_available_vehicles(
                vehicle.category,
                request.start_date,
                request.end_date,
                vehicle.branch_id
            )
            if any(av.id == vehicle.id for av in vehicle_available):
                available_vehicles.append(vehicle)
    
    # Convert to AvailableVehicle response format
    rental_days = (request.end_date - request.start_date).days + 1
    
    results = []
    for vehicle in available_vehicles:
        total_cost = vehicle.daily_rental_rate * rental_days
        
        results.append(AvailableVehicle(
            vehicle_id=vehicle.id,
            category=vehicle.category,
            manufacturer=vehicle.manufacturer,
            model=vehicle.model,
            daily_rental_rate=vehicle.daily_rental_rate,
            number_of_seats=vehicle.number_of_seats,
            branch_id=vehicle.branch_id,
            total_cost=total_cost
        ))
    
    return results