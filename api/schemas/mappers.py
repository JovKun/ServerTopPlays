# Import the necessary library
from pydantic import BaseModel

# User Schema for creating a new mapper
class MapperCreate(BaseModel):
    username: str
    osu_id: int