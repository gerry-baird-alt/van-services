from fastapi import APIRouter, HTTPException
from database import insert_sample_data, delete_data

router = APIRouter(prefix="/admin", tags=["admin"])


@router.delete("/data")
async def delete_all_data():
    """Delete all data from the database (admin only)."""
    delete_data()
    return {"message": "All data deleted successfully"}


@router.post("/reset")
async def reset_database():
    """Reset the database by deleting all existing data and loading sample data (admin only)."""
    try:
        # Reset database state and load sample data
        insert_sample_data()
        return {"message": "Database reset successfully with sample data"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset database: {str(e)}"
        )