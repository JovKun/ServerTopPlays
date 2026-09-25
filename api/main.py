# Import the necessary library
from fastapi import FastAPI

# Initialize routes
from api.routes.players import router as players_router
from api.routes.mappers import router as mappers_router
from api.routes.last_checked import router as last_checked_router

# Initialize the FastAPI application
app = FastAPI()

# Include the routers
app.include_router(players_router, prefix="/api")
app.include_router(mappers_router, prefix="/api")
app.include_router(last_checked_router, prefix="/api")

# Root endpoint for the API
@app.get("/")
async def root():
    return {"message": "Welcome to the Server Top Plays API!"}