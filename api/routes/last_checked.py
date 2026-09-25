# Import the necessary libraries
from fastapi import APIRouter

from db.database import Session
import db.repositories.last_checked as last_checked_repo

# Initialize the router
router = APIRouter()

# Method to retrieve the last checked timestamp
@router.get("/last_checked")
async def get_last_checked_time():
    async with Session() as session:

        # Retrieve the last checked timestamp from the database
        last_checked = await last_checked_repo.get_last_checked_time(session)
        # If no last checked timestamp is found, return a message indicating so
        if not last_checked:
            return {"message": "No last checked timestamp found"}

        # Return the retrieved last checked timestamp
        return {"last_checked": last_checked}

# Method to update the last checked timestamp
@router.put("/last_checked")
async def update_last_checked_time():
    async with Session() as session:

        # Update the last checked timestamp in the database
        await last_checked_repo.update_last_checked_time(session)

        # Return a message indicating that the last checked timestamp has been updated
        return {"message": "Last checked timestamp updated"}