# Import the necessary libraries
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import Player

# Method to get a player by their osu_id
async def get_player_by_osu_id(session: AsyncSession, osu_id: int) -> Player | None:

    # Execute the select query to find the player by osu_id
    result = await session.execute(
        select(Player).where(Player.osu_id == osu_id)
    )

    # Return the first player found or None if no player is found
    return result.scalars().first()

# Method to get a player by their username
async def get_player_by_username(session: AsyncSession, username: str) -> Player | None:

    # Execute the select query to find the player by username
    result = await session.execute(
        select(Player).where(Player.username == username)
    )

    # Return the first player found or None if no player is found
    return result.scalars().first()

# Method to get all players from the database
async def get_all_players(session: AsyncSession) -> list[Player]:

    # Execute the select query to retrieve all players
    result = await session.execute(
        select(Player)
    )

    # Return a list of all players
    return result.scalars().all()

# Method to create a new player in the database
async def create_player_in_db(session: AsyncSession, username: str, osu_id: int) -> Player:

    # Create a new Player instance
    new_player = Player(username=username, osu_id=osu_id)
    session.add(new_player)

    # Add the Player instance to the session and commit the transaction
    await session.commit()
    await session.refresh(new_player)

    # Return the newly created player
    return new_player

# Method to update an existing player's information in the database (only the username can be changed)
async def update_player_in_db(session: AsyncSession, osu_id: int, new_username: str) -> Player | None:

    # Execute the select query to find the player by osu_id
    result = await session.execute(
        select(Player).where(Player.osu_id == osu_id)
    )
    player = result.scalars().first()

    # If the player is found, update their username
    if player:
        player.username = new_username
        await session.commit()
        await session.refresh(player)
        return player

    # Return None if the player was not found
    return None

# Method to delete a player from the database by their osu_id
async def delete_player_by_osu_id(session: AsyncSession, osu_id: int) -> bool:

    # Execute the select query to find the player by osu_id
    result = await session.execute(
        select(Player).where(Player.osu_id == osu_id)
    )
    player = result.scalars().first()

    # If the player is found, delete them from the database
    if player:
        await session.delete(player)
        await session.commit()
        return True

    # Return False if the player was not found
    return False

# Method to delete all players from the database
async def delete_all_players(session: AsyncSession) -> None:

    # Execute the select query to retrieve all players
    result = await session.execute(
        select(Player)
    )
    players = result.scalars().all()

    # If there are players in the database, delete them all
    if players:
        for player in players:
            await session.delete(player)
            await session.commit()