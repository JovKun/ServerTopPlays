# Import the necessary libraries
from fastapi import APIRouter

from api.schemas.mappers import MapperCreate

from db.database import Session
import db.repositories.mappers as mapper_repo

# Initialize the router
router = APIRouter()

# Method to retrieve a mapper by their osu_id
@router.get("/mappers/{osu_id}")
async def get_mapper(osu_id: int):
    async with Session() as session:

        # Retrieve the mapper from the database using their osu_id
        mapper = await mapper_repo.get_mapper_by_osu_id(session, osu_id=osu_id)

        # If the mapper is not found, return a message indicating so
        if not mapper:
            return {"message": "Mapper not found"}

        # Return the retrieved mapper
        return {"mapper": mapper}

# Method to retrieve a mapper by their username
@router.get("/mappers/username/{username}")
async def get_mapper_by_username(username: str):
    async with Session() as session:

        # Retrieve the mapper from the database using their username
        mapper = await mapper_repo.get_mapper_by_username(session, username=username)

        # If the mapper is not found, return a message indicating so
        if not mapper:
            return {"message": "Mapper not found"}

        # Return the retrieved mapper
        return {"mapper": mapper}

# Method to retrieve all mappers from the database
@router.get("/mappers")
async def get_all_mappers():
    async with Session() as session:

        # Retrieve all mappers from the database
        mappers = await mapper_repo.get_all_mappers(session)

        # Return the list of all mappers
        return {"mappers": mappers}

# Method to create a new mapper in the database
@router.post("/mappers")
async def create_mapper(mapper: MapperCreate):
    async with Session() as session:

        # Check if a mapper with the same osu_id already exists
        existing_mapper = await mapper_repo.get_mapper_by_osu_id(session, osu_id=mapper.osu_id)
        if existing_mapper:
            return {"message": "Mapper with this osu_id already exists"}

        # Create a new mapper in the database
        new_mapper = await mapper_repo.create_mapper_in_db(session, username=mapper.username, osu_id=mapper.osu_id)

        # Return the newly created mapper
        return {"mapper": new_mapper}

# Method to update an existing mapper's username in the database
@router.put("/mappers/{osu_id}")
async def update_mapper(osu_id: int, new_username: str):
    async with Session() as session:

        # Update the mapper's username in the database
        updated_mapper = await mapper_repo.update_mapper_in_db(session, osu_id=osu_id, new_username=new_username)

        # If the mapper is not found, return a message indicating so
        if not updated_mapper:
            return {"message": "Mapper not found"}

        # Return the updated mapper
        return {"mapper": updated_mapper}

# Method to delete a mapper by their osu_id
@router.delete("/mappers/{osu_id}")
async def delete_mapper(osu_id: int):
    async with Session() as session:

        # Attempt to delete the mapper from the database using their osu_id
        success = await mapper_repo.delete_mapper_by_osu_id(session, osu_id=osu_id)

        # If the deletion was not successful, return a message indicating so
        if not success:
            return {"message": "Mapper not found or could not be deleted"}

        # Return a success message indicating the mapper was deleted
        return {"message": "Mapper deleted successfully"}

# Method to delete all mappers from the database
@router.delete("/mappers")
async def delete_all_mappers():
    async with Session() as session:

        # Attempt to delete all mappers from the database
        await mapper_repo.delete_all_mappers(session)

        # Return a success message indicating all mappers were deleted
        return {"message": "All mappers deleted successfully"}