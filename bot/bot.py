# Import the necessary libraries
from datetime import datetime, timezone

import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_ANNOUNCE_CHANNEL_ID = int(os.getenv("DISCORD_ANNOUNCE_CHANNEL_ID"))
DISCORD_BEATMAP_CHANNEL_ID = int(os.getenv("DISCORD_BEATMAP_CHANNEL_ID"))
DISCORD_GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))

OSU_CLIENT_ID = os.getenv("OSU_CLIENT_ID")
OSU_CLIENT_SECRET = os.getenv("OSU_CLIENT_SECRET")

# discord.py
import discord
from discord.ext import tasks

# osu.py
from osu import AsynchronousClient

# Repositories
from db.database import Session
import db.repositories.mappers as mapper_repo
import db.repositories.players as player_repo
import db.repositories.last_checked as last_checked_repo

# osu commands
from bot.top_plays import check_new_beatmaps, check_top_plays

# Intents are required to access certain events and data from Discord
intents = discord.Intents.default()
intents.message_content = True

# Create a Discord client instance with the specified intents and the command tree
discord_client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(discord_client)

# Create an osu! API client instance using the provided client ID and secret
osu_client = AsynchronousClient.from_credentials(OSU_CLIENT_ID, OSU_CLIENT_SECRET, redirect_url=None, request_wait_time=0)

# ====================
# Events
# ====================

# Event that triggers when the bot is ready and connected to Discord
@discord_client.event
async def on_ready():
    """
    Event triggered when the bot is ready and connected to Discord.
    """

    print(f"Logged in as {discord_client.user} (ID: {discord_client.user.id})")
    print("------")

    # Sync the command tree with Discord
    synced =await tree.sync(guild=discord.Object(id=DISCORD_GUILD_ID))
    print(f"Command tree synced ({len(synced)} commands).")

    # Create playing status message
    await discord_client.change_presence(activity=discord.Game(name="osu!"))

    # Start the event looper
    if not event_looper.is_running():
        event_looper.start()

# Event looper that runs the listeners every 2 minutes
@tasks.loop(minutes=2)
async def event_looper():
    """
    Event looper that runs the listeners every 2 minutes.
    """

    print(f"Running event looper at {datetime.now(timezone.utc)}")

    try:
        # Uncomment these lines once the functions are implemented
        await check_new_beatmaps(discord_client, osu_client, DISCORD_BEATMAP_CHANNEL_ID)
        await check_top_plays(discord_client, osu_client, DISCORD_ANNOUNCE_CHANNEL_ID)
        pass

    # If an exception occurs during the execution of the event looper, print the error message and return
    except Exception as e:
        print(f"Error in event looper: {e}")
        return

    # Update the last_checked timestamp in the database
    async with Session() as session:
        await last_checked_repo.update_last_checked_time(session)

# Fun messages when something is mentioned
@discord_client.event
async def on_message(message):
    """
    Event triggered when a message is sent in a channel the bot has access to.
    """

    # Ignore messages sent by the bot itself
    if message.author == discord_client.user:
        return

    # If the bot is mentioned in a message, respond with a fun message
    if message.content.startswith('pp'):
        await message.channel.send('give pp for the pp god')
    elif message.content.startswith('hi'):
        await message.channel.send('whats good uncle')

# ====================
# Commands
# ====================

### /top ###
# Command to get the top 10 plays of a player by their username
# Usage: /top <username>
# Parameters: username <str> - The user to get the top 10 plays for
@tree.command(
    name = "top",
    description = "Get the top 10 plays of a player",
    guild = discord.Object(id=DISCORD_GUILD_ID)
)
@discord.app_commands.describe(username="The user to get the top 10 plays for")
async def top(inter: discord.Interaction, username: str):

    # Defer the response to give the bot more time to process the command
    await inter.response.defer()

    # Get the user
    async with Session() as session:
        user = await player_repo.get_player_by_username(session, username=username)

    if not user:
        await inter.followup.send(f"User '{username}' not found.")
        return

    # Get the user from the osu! API
    osu_user = await osu_client.get_user(user.osu_id, mode="osu")

    # Print a simple embed message
    embed = discord.Embed(
        title = f"**{osu_user.username}'s Top Plays**",
        description = f"{osu_user.statistics.pp}pp (#{osu_user.statistics.global_rank} {osu_user.country_code}#{osu_user.statistics.country_rank})",
        color = 0x158ddc,
        url = f"https://osu.ppy.sh/users/{osu_user.id}",
        timestamp = datetime.now()
    )

    # Set the thumbnail of the embed to the user's avatar
    embed.set_thumbnail(url = osu_user.avatar_url)

    # Get the user_scores
    user_scores = await osu_client.get_user_scores(user.osu_id, mode="osu", type="best", limit=10)
    user_score_beatmaps = await osu_client.get_beatmaps([score.beatmap_id for score in user_scores])
    user_score_max_combos = {beatmap.id: beatmap.max_combo for beatmap in user_score_beatmaps}

    # Add the fields to the embed
    for ind, score in enumerate(user_scores):
            
        # Set the values of each data
        user_pp = round(score.pp, 2)
        user_accuracy = round(score.accuracy * 100, 2)
            
        # ex. current_user.mods = [LazerMod(mod = "HR", settings = None), LazerMod(mod = "DT", settings = None)]
        user_mods = "".join([lazermod.mod.value for lazermod in score.mods])
        user_mods = user_mods if user_mods != "" else "NM"
    
        # ex. current_user.rank = ScoreRank.SILVER_S
        user_rank = score.rank.value
    
        # Change the user_rank to the specific emoji
        if user_rank == "D":
            user_rank = "<:D_nn:1330334959222788236>"
        elif user_rank == "C":
            user_rank = "<:C_nn:1330334958027538513>"
        elif user_rank == "B":
            user_rank = "<:B_nn:1330334956961923143>"
        elif user_rank == "A":
            user_rank = "<:A_nn:1330334955418681345>"
        elif user_rank == "S":
            user_rank = "<:S_nn:1330334960460103722>"
        elif user_rank == "SH":
            user_rank = "<:SH_nn:1330334960460103722>"
        elif user_rank == "X":
            user_rank = "<:SS_nn:1330334962972364873>"
        elif user_rank == "XH":
            user_rank = "<:SSH_nn:1330334962972364873>"

        # Get the difficulty rating of the beatmap
        star_rate = round(score.beatmap.difficulty_rating, 2)

        # Get the miss count of the score
        count_miss = "" if score.statistics.miss is None else str(score.statistics.miss) + "<:miss_nn:1330340826492047481>"

        # Add the field to the embed
        embed.add_field(
            name="\u200b", # Invisible name for spacing
            value=f"#{ind + 1} - **[{score.beatmapset.title} [{score.beatmap.version}]]({score.beatmap.url})** [{star_rate}★]\n{user_rank} **{user_pp}pp** ({user_accuracy}%) [**{score.max_combo}x**/{user_score_max_combos[score.beatmap_id]}x] {count_miss} \n+**{user_mods}** <t:{int(score.ended_at.timestamp())}:R>",
            inline=False
        )

    # Send the embed
    await inter.followup.send(embed=embed)

### /register_player ###
# Command to register a player to the bot
# Usage: /register_player <username>
# Parameters: username <str> - The osu! username to register
@tree.command(
    name = "register",
    description = "Register a player to the bot",
    guild = discord.Object(id=DISCORD_GUILD_ID)
)
@discord.app_commands.describe(username="The osu! username to register")
async def register_player(inter: discord.Interaction, username: str):

    # Check if the user is already registered in the database
    async with Session() as session:
        existing_player = await player_repo.get_player_by_username(session, username=username)

    if existing_player:
        await inter.response.send_message(f"User '{username}' is already registered.")
        return

    # Get the user from the osu! API
    osu_user = await osu_client.get_user(username, mode="osu")

    # Check if the user exists in the osu! API
    if not osu_user:
        await inter.response.send_message(f"User '{username}' not found in osu! API.")
        return

    # Create the player in the database
    async with Session() as session:
        new_player = await player_repo.create_player_in_db(
            session, 
            username=osu_user.username, 
            osu_id=osu_user.id
        )

    # Send a confirmation message
    await inter.response.send_message(f"User '{new_player.username}' has been registered with osu! ID {new_player.osu_id}.")

### /unregister_player ###
# Command to unregister a player from the bot
# Usage: /unregister_player <username>
# Parameters: username <str> - The osu! username to unregister
@tree.command(
    name = "unregister",
    description = "Unregister a player from the bot",
    guild = discord.Object(id=DISCORD_GUILD_ID)
)
@discord.app_commands.describe(username="The osu! username to unregister")
async def unregister_player(inter: discord.Interaction, username: str):

    # Check if the user is registered in the database
    async with Session() as session:
        existing_player = await player_repo.get_player_by_username(session, username=username)

    if not existing_player:
        await inter.response.send_message(f"User '{username}' is not registered.")
        return

    # Delete the player from the database
    async with Session() as session:
        success = await player_repo.delete_player_by_osu_id(session, osu_id=existing_player.osu_id)

    if success:
        await inter.response.send_message(f"User '{username}' has been unregistered.")
    else:
        await inter.response.send_message(f"Failed to unregister user '{username}'. Please try again later.")

### /register_mapper ###
# Command to register a mapper to the bot
# Usage: /register_mapper <username>
# Parameters: username <str> - The osu! username to register
@tree.command(
    name = "register_mapper",
    description = "Register a mapper to the bot",
    guild = discord.Object(id=DISCORD_GUILD_ID)
)
@discord.app_commands.describe(username="The osu! username to register as a mapper")
async def register_mapper(inter: discord.Interaction, username: str):

    # Check if the user is already registered as a mapper in the database
    async with Session() as session:
        existing_mapper = await mapper_repo.get_mapper_by_username(session, username=username)

    if existing_mapper:
        await inter.response.send_message(f"Mapper '{username}' is already registered.")
        return

    # Get the user from the osu! API
    osu_user = await osu_client.get_user(username, mode="osu")

    # Check if the user exists in the osu! API
    if not osu_user:
        await inter.response.send_message(f"User '{username}' not found in osu! API.")
        return

    # Create the mapper in the database
    async with Session() as session:
        new_mapper = await mapper_repo.create_mapper_in_db(
            session, 
            username=osu_user.username, 
            osu_id=osu_user.id
        )

    # Send a confirmation message
    await inter.response.send_message(f"Mapper '{new_mapper.username}' has been registered with osu! ID {new_mapper.osu_id}.")

### /unregister_mapper ###
# Command to unregister a mapper from the bot
# Usage: /unregister_mapper <username>
# Parameters: username <str> - The osu! username to unregister
@tree.command(
    name = "unregister_mapper",
    description = "Unregister a mapper from the bot",
    guild = discord.Object(id=DISCORD_GUILD_ID)
)
@discord.app_commands.describe(username="The osu! username to unregister as a mapper")
async def unregister_mapper(inter: discord.Interaction, username: str):

    # Check if the user is registered as a mapper in the database
    async with Session() as session:
        existing_mapper = await mapper_repo.get_mapper_by_username(session, username=username)

    if not existing_mapper:
        await inter.response.send_message(f"Mapper '{username}' is not registered.")
        return

    # Delete the mapper from the database
    async with Session() as session:
        success = await mapper_repo.delete_mapper_by_osu_id(session, osu_id=existing_mapper.osu_id)

    if success:
        await inter.response.send_message(f"Mapper '{username}' has been unregistered.")
    else:
        await inter.response.send_message(f"Failed to unregister mapper '{username}'. Please try again later.")

### /list_players ###
# Command to list all registered players
# Usage: /list_players
# Parameters: None
@tree.command(
    name = "list_players",
    description = "List all registered players",
    guild = discord.Object(id=DISCORD_GUILD_ID)
)
async def list_players(inter: discord.Interaction):

    # Get all registered players from the database
    async with Session() as session:
        players = await player_repo.get_all_players(session)

    if not players:
        await inter.response.send_message("No players are currently registered.")
        return

    # Create a list of player usernames
    player_list = "\n".join([player.username for player in players])

    # Send the list of registered players
    await inter.response.send_message(f"Registered Players:\n{player_list}")

### /list_mappers ###
# Command to list all registered mappers
# Usage: /list_mappers
# Parameters: None
@tree.command(
    name = "list_mappers",
    description = "List all registered mappers",
    guild = discord.Object(id=DISCORD_GUILD_ID)
)
async def list_mappers(inter: discord.Interaction):

    # Get all registered mappers from the database
    async with Session() as session:
        mappers = await mapper_repo.get_all_mappers(session)

    if not mappers:
        await inter.response.send_message("No mappers are currently registered.")
        return

    # Create a list of mapper usernames
    mapper_list = "\n".join([mapper.username for mapper in mappers])

    # Send the list of registered mappers
    await inter.response.send_message(f"Registered Mappers:\n{mapper_list}")

### /leaderboard ###
# Command to list the top 10 scores of all registered players
# Usage: /leaderboard
# Parameters: None
@tree.command(
    name = "leaderboard",
    description = "List the top 10 scores of all registered players",
    guild = discord.Object(id=DISCORD_GUILD_ID)
)
async def leaderboard(inter: discord.Interaction):

    # Defer the response
    await inter.response.defer()

    # Get all registered players from the database
    async with Session() as session:
        players = await player_repo.get_all_players(session)

    if not players:
        await inter.followup.send("No players are currently registered.")
        return

    # Create a list to hold the top scores
    top_plays = []

    # Get the top score for each registered player
    for player in players:

        # Get the user from the osu! API
        osu_user = await osu_client.get_user(player.osu_id, mode="osu")

        # Get the user's top score
        user_scores = await osu_client.get_user_scores(player.osu_id, mode="osu", type="best", limit=10)

        # If the top_plays list is empty, set the top plays to the user's top scores
        if len(top_plays) == 0:
            top_plays = user_scores
        else:

            # Extend the top_plays list with the user's top scores
            top_plays.extend(user_scores)

            # Sort the top_plays list by pp in descending order and keep only the top 10 scores
            top_plays.sort(key=lambda score: score.pp, reverse=True)

            # Keep only the top 10 scores
            top_plays = top_plays[:10]

    # Get all the beatmaps of the top plays
    user_beatmaps = await osu_client.get_beatmaps([score.beatmap_id for score in top_plays])

    # Get the max combos of the beatmaps
    beatmap_max_combos = {beatmap.id: beatmap.max_combo for beatmap in user_beatmaps}

    # Print a simple embed message
    embed = discord.Embed(
        title = f"**Top 10 Plays in the Server**",
        color = 0x158ddc,
        timestamp = datetime.now()
    )

    # Loop through the top plays and add them to the embed
    for ind, score in enumerate(top_plays):

        # Set the values of each data
        user_pp = round(score.pp, 2)
        user_accuracy = round(score.accuracy * 100, 2)
        
        # ex. current_user.mods = [LazerMod(mod = "HR", settings = None), LazerMod(mod = "DT", settings = None)]
        user_mods = "".join([lazermod.mod.value for lazermod in score.mods])
        user_mods = user_mods if user_mods != "" else "NM"

        # ex. current_user.rank = ScoreRank.SILVER_S
        user_rank = score.rank.value

        # Change the user_rank to the specific emoji
        if user_rank == "D":
            user_rank = "<:D_nn:1330334959222788236>"
        elif user_rank == "C":
            user_rank = "<:C_nn:1330334958027538513>"
        elif user_rank == "B":
            user_rank = "<:B_nn:1330334956961923143>"
        elif user_rank == "A":
            user_rank = "<:A_nn:1330334955418681345>"
        elif user_rank == "S":
            user_rank = "<:S_nn:1330334960460103722>"
        elif user_rank == "SH":
            user_rank = "<:SH_nn:1330334960460103722>"
        elif user_rank == "X":
            user_rank = "<:SS_nn:1330334962972364873>"
        elif user_rank == "XH":
            user_rank = "<:SSH_nn:1330334962972364873>"

        # Get the difficulty rating of the beatmap
        star_rate = round(score.beatmap.difficulty_rating, 2)

        # Get the miss count of the score
        count_miss = "" if score.statistics.miss is None else str(score.statistics.miss) + "<:miss_nn:1330340826492047481>"

        # Add the field to the embed
        embed.add_field(
            name = f"**{score.user.username}**",
            value = f"#{ind + 1} - **[{score.beatmapset.title} [{score.beatmap.version}]]({score.beatmap.url})** [{star_rate}★]\n{user_rank} **{user_pp}pp** ({user_accuracy}%) [**{score.max_combo}x**/{beatmap_max_combos[score.beatmap_id]}x] {count_miss} \n+**{user_mods}** <t:{int(score.ended_at.timestamp())}:R>",
            inline = False
        )

    # Send the embed
    await inter.followup.send(embed=embed)