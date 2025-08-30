from fastapi import APIRouter, HTTPException
from typing import List
from model import Vehicle, VehicleCreate
from database import VehicleDB
from database.models import BranchDB

router = APIRouter(prefix="/vehicle", tags=["vehicles"])


@router.get("", response_model=List[Vehicle])
async def get_vehicles():
    """
    Get all vehicles in the rental fleet.
    
    Returns a list of all vehicles with their details including:
    - Vehicle specifications (category, manufacturer, model)
    - Pricing information (daily rental rate)
    - Capacity (number of seats)
    - Branch location assignment
    """
    return VehicleDB.get_all()


@router.get("/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(vehicle_id: int):
    """
    Get a specific vehicle by its ID.
    
    Args:
        vehicle_id: The unique identifier of the vehicle
        
    Returns:
        Vehicle details including specifications, pricing, and branch assignment
        
    Raises:
        HTTPException: 404 if vehicle with the specified ID is not found
    """
    vehicle = VehicleDB.get_by_id(vehicle_id)
    if vehicle:
        return vehicle
    raise HTTPException(status_code=404, detail="Vehicle not found")


@router.post("", response_model=Vehicle)
async def create_vehicle(vehicle_data: VehicleCreate):
    """
    Add a new vehicle to the rental fleet.
    
    Creates a new vehicle record with the provided specifications and assigns it to a branch.
    The vehicle will be available for booking once created.
    
    Args:
        vehicle_data: Vehicle creation data including:
            - category: Vehicle size category (e.g., "Small", "Medium", "Large")
            - manufacturer: Vehicle manufacturer name
            - model: Vehicle model name
            - daily_rental_rate: Daily rental price in decimal format
            - number_of_seats: Passenger capacity
            - branch_id: ID of the branch where vehicle will be located
            
    Returns:
        The created vehicle with assigned ID and all specifications
        
    Raises:
        HTTPException: 400 if the specified branch ID does not exist
    """
    # Validate that the branch exists
    branch = BranchDB.get_by_id(vehicle_data.branch_id)
    if not branch:
        raise HTTPException(status_code=400, detail=f"Branch with ID {vehicle_data.branch_id} does not exist")
    
    vehicle = Vehicle(
        id=0,  # Will be set by database
        category=vehicle_data.category,
        manufacturer=vehicle_data.manufacturer,
        model=vehicle_data.model,
        daily_rental_rate=vehicle_data.daily_rental_rate,
        number_of_seats=vehicle_data.number_of_seats,
        branch_id=vehicle_data.branch_id
    )
    return VehicleDB.create(vehicle)