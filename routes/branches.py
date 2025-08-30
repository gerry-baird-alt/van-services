from fastapi import APIRouter, HTTPException
from typing import List
from model import Branch, BranchCreate
from database.models import BranchDB

router = APIRouter(prefix="/branches", tags=["branches"])


@router.get("/", response_model=List[Branch])
async def get_all_branches():
    """Get all branches."""
    return BranchDB.get_all()


@router.get("/{branch_id}", response_model=Branch)
async def get_branch(branch_id: int):
    """Get a branch by ID."""
    branch = BranchDB.get_by_id(branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch


@router.post("/", response_model=Branch)
async def create_branch(branch: BranchCreate):
    """Create a new branch."""
    new_branch = Branch(branch_id=0, **branch.dict())
    return BranchDB.create(new_branch)