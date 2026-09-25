# Import the necessary library
from pydantic import BaseModel

# User Schema for creating a new player
class PlayerCreate(BaseModel):
    username: str
    osu_id: int