# Import the necessary libraries
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

from bot.bot import discord_client

if __name__ == "__main__":
    discord_client.run(DISCORD_TOKEN)