# Import the necessary libraries
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import Mapper

# Method to get a mapper by their osu_id
async def get_mapper_by_osu_id(session: AsyncSession, osu_id: int) -> Mapper | None:

    # Execute the select query to find the mapper by osu_id
    result = await session.execute(
        select(Mapper).where(Mapper.osu_id == osu_id)
    )

    # Return the first mapper found or None if no mapper is found
    return result.scalars().first()

# Method to get a mapper by their username
async def get_mapper_by_username(session: AsyncSession, username: str) -> Mapper | None:

    # Execute the select query to find the mapper by username
    result = await session.execute(
        select(Mapper).where(Mapper.username == username)
    )

    # Return the first mapper found or None if no mapper is found
    return result.scalars().first()

# Method to get all mappers from the database
async def get_all_mappers(session: AsyncSession) -> list[Mapper]:

    # Execute the select query to retrieve all mappers
    result = await session.execute(
        select(Mapper)
    )

    # Return a list of all mappers
    return result.scalars().all()

# Method to create a new mapper in the database
async def create_mapper_in_db(session: AsyncSession, username: str, osu_id: int) -> Mapper:

    # Create a new Mapper instance
    new_mapper = Mapper(username=username, osu_id=osu_id)
    session.add(new_mapper)

    # Add the Mapper instance to the session and commit the transaction
    await session.commit()
    await session.refresh(new_mapper)

    # Return the newly created mapper
    return new_mapper

# Method to update an existing mapper's information in the database (only the username can be changed)
async def update_mapper_in_db(session: AsyncSession, osu_id: int, new_username: str) -> Mapper | None:

    # Execute the select query to find the mapper by osu_id
    result = await session.execute(
        select(Mapper).where(Mapper.osu_id == osu_id)
    )

    # Retrieve the first mapper found or None if no mapper is found
    mapper = result.scalars().first()

    # If a mapper is found, update their username and commit the transaction
    if mapper:
        mapper.username = new_username
        await session.commit()
        await session.refresh(mapper)

    # Return the updated mapper or None if no mapper was found
    return mapper

# Method to delete a mapper by their osu_id
async def delete_mapper_by_osu_id(session: AsyncSession, osu_id: int) -> bool:

    # Execute the select query to find the mapper by osu_id
    result = await session.execute(
        select(Mapper).where(Mapper.osu_id == osu_id)
    )

    # Retrieve the first mapper found or None if no mapper is found
    mapper = result.scalars().first()

    # If a mapper is found, delete them from the database and commit the transaction
    if mapper:
        await session.delete(mapper)
        await session.commit()
        return True

    # Return False if no mapper was found to delete
    return False

# Method to delete all mappers from the database
async def delete_all_mappers(session: AsyncSession) -> None:
    
    # Execute the select query to retrieve all mappers
    result = await session.execute(
        select(Mapper)
    )
    mappers = result.scalars().all()

    # If there are mappers in the database, delete them all
    if mappers:
        for mapper in mappers:
            await session.delete(mapper)
            await session.commit()
