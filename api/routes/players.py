# Import the necessary libraries
from fastapi import APIRouter

from api.schemas.players import PlayerCreate

from db.database import Session
import db.repositories.players as player_repo

# Initialize the router
router = APIRouter()

# Method to retrieve a player by their osu_id
@router.get("/players/{osu_id}")
async def get_player(osu_id: int):
    async with Session() as session:

        # Retrieve the player from the database using their osu_id
        player = await player_repo.get_player_by_osu_id(session, osu_id=osu_id)

        # If the player is not found, return a message indicating so
        if not player:
            return {"message": "Player not found"}

        # Return the retrieved player
        return {"player": player}

# Method to retrieve a player by their username
@router.get("/players/username/{username}")
async def get_player_by_username(username: str):
    async with Session() as session:

        # Retrieve the player from the database using their username
        player = await player_repo.get_player_by_username(session, username=username)

        # If the player is not found, return a message indicating so
        if not player:
            return {"message": "Player not found"}

        # Return the retrieved player
        return {"player": player}

# Method to retrieve all players from the database
@router.get("/players")
async def get_all_players():
    async with Session() as session:

        # Retrieve all players from the database
        players = await player_repo.get_all_players(session)

        # Return the list of all players
        return {"players": players}

# Method to create a new player in the database
@router.post("/players")
async def create_player(player: PlayerCreate):
    async with Session() as session:

        # Check if a player with the same osu_id already exists
        existing_player = await player_repo.get_player_by_osu_id(session, osu_id=player.osu_id)
        if existing_player:
            return {"message": "Player with this osu_id already exists"}

        # Create a new player in the database
        new_player = await player_repo.create_player_in_db(session, username=player.username, osu_id=player.osu_id)

        # Return the newly created player
        return {"player": new_player}

# Method to change a player's username in the database
@router.put("/players/{osu_id}")
async def update_player(osu_id: int, new_username: str):
    async with Session() as session:

        # Update the player's username in the database
        updated_player = await player_repo.update_player_in_db(session, osu_id=osu_id, new_username=new_username)

        # If the player is not found, return a message indicating so
        if not updated_player:
            return {"message": "Player not found"}

        # Return the updated player
        return {"player": updated_player}

# Method to delete a player from the database using their osu_id
@router.delete("/players/{osu_id}")
async def delete_player(osu_id: int):
    async with Session() as session:

        # Attempt to delete the player from the database using their osu_id
        success = await player_repo.delete_player_by_osu_id(session, osu_id=osu_id)

        # If the deletion was not successful, return a message indicating so
        if not success:
            return {"message": "Player not found or could not be deleted"}

        # Return a success message indicating the player was deleted
        return {"message": "Player deleted successfully"}

# Method to delete all players from the database
@router.delete("/players")
async def delete_all_players():
    async with Session() as session:

        # Attempt to delete all players from the database
        await player_repo.delete_all_players(session)

        # Return a success message indicating all players were deleted
        return {"message": "All players deleted successfully"}