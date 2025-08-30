from pydantic import BaseModel, ConfigDict


class Branch(BaseModel):
    model_config = ConfigDict()
    
    branch_id: int
    branch_name: str
    address: str


class BranchCreate(BaseModel):
    model_config = ConfigDict()
    
    branch_name: str
    address: str