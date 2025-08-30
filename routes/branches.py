from fastapi import APIRouter, HTTPException
from typing import List
from model import Branch, BranchCreate
from database.models import BranchDB

router = APIRouter(prefix="/branches", tags=["branches"])


@router.get("/", response_model=List[Branch])
async def get_all_branches():
    """
    Get all branch locations in the rental network.
    
    Returns a complete list of all physical rental locations where
    customers can pick up and return vehicles. Each branch includes
    location details and contact information.
    
    Returns:
        List of Branch objects containing:
            - Branch identification and name
            - Complete address information
            - City location for geographic reference
    """
    return BranchDB.get_all()


@router.get("/{branch_id}", response_model=Branch)
async def get_branch(branch_id: int):
    """
    Get a specific branch location by its ID.
    
    Retrieves detailed information for a single rental branch location
    including address, city, and operational details.
    
    Args:
        branch_id: The unique identifier of the branch location
        
    Returns:
        Branch object with complete location details:
            - Branch name and identification
            - Full street address
            - City location
            
    Raises:
        HTTPException: 404 if branch with the specified ID is not found
    """
    branch = BranchDB.get_by_id(branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch


@router.post("/", response_model=Branch)
async def create_branch(branch: BranchCreate):
    """
    Create a new branch location in the rental network.
    
    Establishes a new physical location where customers can pick up and
    return rental vehicles. The new branch will be available for vehicle
    assignments and bookings immediately upon creation.
    
    Args:
        branch: BranchCreate containing:
            - branch_name: Descriptive name for the location
            - address: Complete street address
            - city: City where the branch is located
            
    Returns:
        Created Branch object with assigned ID and all location details
        
    Note:
        The new branch can immediately be assigned vehicles and used for bookings.
        Ensure address information is accurate for customer navigation.
    """
    new_branch = Branch(branch_id=0, **branch.dict())
    return BranchDB.create(new_branch)