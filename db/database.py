# Import necessary libraries
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)

# Load environment variables from the .env file
load_dotenv()

# Initialize the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)

# Create an asynchronous session maker
Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)