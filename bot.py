# Description: A Discord bot that detects whenever a registered osu! user submits a play within their top 10 plays.
# The bot will then send an embed message to a specified channel with the details of the play.
#
# Author: nnull. (Jovian Kuntjoro)
# Date: 2025-01-18

#################
### LIBRARIES ###
#################

# For discord.py API
import discord
from discord import app_commands
from discord.ext import tasks

# For osu! API
from osu import Client

# For keeping track of time
import datetime

# For reading the config file
import json

# Keep the bot alive
from keep_alive import keep_alive
keep_alive()

# Intents are required to access certain events
intents = discord.Intents.default()
intents.message_content = True

# Load the config file
with open('config.json') as f:
    config = json.load(f)

# Create a new client for discord
client = discord.Client(intents=intents)

# Create a new osu! client
osu_client = Client.from_credentials(config['osu']['client_id'], config['osu']['client_secret'], None)

# Create a new command tree
tree = app_commands.CommandTree(client)

# Event that triggers when the bot is ready
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    # Sync the command tree
    await tree.sync(guild = discord.Object(id = config['discord']['guild_id']))
    print("Synced!")

    # Create playing status to osu!
    await client.change_presence(activity = discord.Game(name = "osu!"))

    # Start the event looper
    event_looper.start()

# Event looper that runs the listeners every 2 minutes
@tasks.loop(minutes = 2)
async def event_looper():
    
    # Get the current time
    current_time = datetime.datetime.now(datetime.timezone.utc)

    # Check for new beatmaps and top plays
    await client.loop.run_in_executor(None, check_new_beatmaps)
    await client.loop.run_in_executor(None, check_top_plays)

    # Write the current time to the config file to store as a "last checked" time
    config["last_checked"] = current_time.timestamp()
    
    # Check if this is getting run
    print("Finished checking for new beatmaps and top plays...")

    # Save the changes to the config file
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4, sort_keys=True, separators=(',', ': '))

# Event that triggers when a message is sent
@client.event
async def on_message(message):
    if message.content.startswith('hello'):
        await message.channel.send('Hello!')

#################
### FUNCTIONS ###
#################

### CHECK_NEW_BEATMAPS FUNCTION ###
# Event listener to check whether a user has submitted a new beatmap
def check_new_beatmaps():

    # Check if this is getting run
    print("Checking new beatmaps...")

    # Get the new beatmaps of each user
    for mapper in config['users']['mappers']:

        # Debug
        print(f"Checking {mapper}'s new beatmaps...")

        # Get the user
        current_mapper = osu_client.get_user(mapper)

        # Get the user_beatmaps
        user_beatmapsets = osu_client.get_user_beatmaps(current_mapper.id, type = "pending", limit = 3)

        # Check if any of the user_beatmaps are made
        for beatmapset in user_beatmapsets:

            # Get the time the beatmap was made
            beatmap_time = beatmapset.last_updated

            # Check if the beatmap was made from now to last checked
            if beatmap_time.timestamp() > config['last_checked']:

                # Get beatmapset status
                beatmap_status = ""

                if beatmapset.status == -1:
                    beatmap_status = "WIP"
                elif beatmapset.status == 0:
                    beatmap_status = "Pending"
                else:

                    # If updated, then it could only be WIP or Pending
                    beatmap_status = ""

                # Get whether the beatmap is submitted or just updated
                beatmap_status_2 = ""

                if beatmapset.submitted_date.timestamp() > config['last_checked']:
                    beatmap_status_2 = "submitted a new"
                else:
                    beatmap_status_2 = "updated their"                

                # Print a simple embed message
                embed = discord.Embed(
                    title = f"**{current_mapper.username} just {beatmap_status_2} beatmap!**",
                    description = f"**[{beatmapset.title}](https://osu.ppy.sh/beatmapsets/{beatmapset.id})**\nStatus: {beatmap_status}\nHypes: {beatmapset.hype.current}/{beatmapset.hype.required}\n{beatmapset.favourite_count} :heart: {beatmapset.play_count} :arrow_forward:",
                    color = 0x158ddc,
                    timestamp = datetime.datetime.now()
                )

                # Create a list of all the difficulties
                for diff in beatmapset.beatmaps:

                    # Add the field to the embed
                    embed.add_field(
                        name=f"**{diff.version}**\n{diff.difficulty_rating:.2f}★",
                        value="\u200B",
                        inline=True
                    )

                # Set the thumbnail of the embed
                embed.set_thumbnail(url = current_mapper.avatar_url)

                # Add thumbnail to show the beatmap background
                embed.set_image(url = f"{beatmapset.background_url}")

                # Send the embed message to the specified channel
                channel = client.get_channel(config['discord']['beatmap_channel_id'])
                client.loop.create_task(channel.send(embed = embed))

    print("Finished checking new beatmaps...")

### CHECK_TOP_PLAYS FUNCTION ###
# Event listener to check whether a user has submitted a new top 10 play
def check_top_plays():

    # Check if this is getting run
    print("Checking top plays...")

    # Get the top 10 plays of each user
    for user in config['users']['players']:

        # Debug
        print(f"Checking {user}'s top plays...")
        
        # Get the user
        current_user = osu_client.get_user(user)

        # Get the user_scores
        user_scores = osu_client.get_user_scores(current_user.id, type = "best", mode = "osu", limit = 10)

        # Check if any of the user_scores are made
        for ind, score in enumerate(user_scores):

            # Get the time the play was made
            play_time = score.ended_at

            # Check if the play was made from now to last checked
            if play_time.timestamp() > config['last_checked']:

                # Print a simple embed message
                embed = discord.Embed(
                    title = f"**{current_user.username} just set a new top play! ({round(score.pp, 2)}pp)**",
                    description = f"{current_user.statistics.pp}pp (#{current_user.statistics.global_rank} {current_user.country_code}#{current_user.statistics.country_rank})",
                    color = 0x158ddc,
                    url = f"https://osu.ppy.sh/users/{current_user.id}",
                    timestamp = datetime.datetime.now()
                )

                # Set the thumbnail of the embed
                embed.set_thumbnail(url = current_user.avatar_url)

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

                # Get the max combo of the beatmap
                user_beatmap = osu_client.get_beatmap(score.beatmap_id)
                beatmap_max_combo = user_beatmap.max_combo

                # Get the miss count of the score
                count_miss = "" if score.statistics.miss is None else str(score.statistics.miss) + "<:miss_nn:1330340826492047481>"

                # Add the field to the embed
                embed.add_field(
                    name="__Personal Best #" + str(ind + 1) + "__",
                    value=f"**[{score.beatmapset.title} [{score.beatmap.version}]]({score.beatmap.url})** [{star_rate}★]\n{user_rank} **{user_pp}pp** ({user_accuracy}%) [**{score.max_combo}x**/{beatmap_max_combo}x] {count_miss} \n+**{user_mods}** <t:{int(score.ended_at.timestamp())}:R>\n",
                    inline=False
                )

                # Add another field to show the link to the play
                embed.add_field(
                    name="\u200B",
                    value=f"[Link to Score](https://osu.ppy.sh/scores/{score.id})",
                )

                # Add thumbnail to show the beatmap background
                embed.set_image(url = f"https://assets.ppy.sh/beatmaps/{score.beatmapset.id}/covers/raw.jpg")

                # Send the embed message to the specified channel
                channel = client.get_channel(config['discord']['announcement_channel_id'])
                client.loop.create_task(channel.send(embed = embed))

    print("Finished checking top plays...")

################
### COMMANDS ###
################

### /TOP COMMAND ###
# Command to get the top 10 plays of a user
# Usage: /top <user>
# Parameters: user <str> - The user to get the top plays of
@tree.command(
    name = "top",
    description = "Get the top 10 plays of a user",
    guild = discord.Object(id = config['discord']['guild_id'])
)
@app_commands.describe(user = "The user to get the top plays of")
async def top(inter, user: str):

    # Defer the response
    await inter.response.defer()

    # Get the user
    current_user = osu_client.get_user(user)

    # Check if the user exists
    if current_user is None:
        await inter.response.send_message("User not found!")
        return

    # Print a simple embed message
    embed = discord.Embed(
        title = f"**{current_user.username}'s Top Plays**",
        description = f"{current_user.statistics.pp}pp (#{current_user.statistics.global_rank} {current_user.country_code}#{current_user.statistics.country_rank})",
        color = 0x158ddc,
        url = f"https://osu.ppy.sh/users/{current_user.id}",
        timestamp = datetime.datetime.now()
    )

    # Set the thumbnail of the embed
    embed.set_thumbnail(url = current_user.avatar_url)

    # Get the user_scores
    user_scores = osu_client.get_user_scores(current_user.id, type = "best", mode = "osu", limit = 10)

    # Get all the beatmaps of the user_scores
    user_beatmaps = osu_client.get_beatmaps([score.beatmap_id for score in user_scores])

    # Get the max combos of the beatmaps
    beatmap_max_combos = {beatmap.id: beatmap.max_combo for beatmap in user_beatmaps}

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
            name="\u200b",
            value=f"#{ind + 1} - **[{score.beatmapset.title} [{score.beatmap.version}]]({score.beatmap.url})** [{star_rate}★]\n{user_rank} **{user_pp}pp** ({user_accuracy}%) [**{score.max_combo}x**/{beatmap_max_combos[score.beatmap_id]}x] {count_miss} \n+**{user_mods}** <t:{int(score.ended_at.timestamp())}:R>",
            inline=False
        )

    # Send the embed
    await inter.followup.send(embed=embed)

### /REGISTER COMMAND ###
# Command to register a user to the bot, so that the bot can track their plays
# Usage: /register <user>
# Parameters: user <str> - The user to register
@tree.command(
    name = "register",
    description = "Add a user for the bot to track",
    guild = discord.Object(id = config['discord']['guild_id'])
)
@app_commands.describe(user = "The user to register")
async def register(inter, user: str):

    # Get the user
    current_user = osu_client.get_user(user)

    # Check if the user exists
    if current_user is None:
        await inter.response.send_message("User not found!")
        return
    
    # Check if the user is already registered
    if user in config['users']['players']:
        await inter.response.send_message("User is already registered!")
        return
    
    # Add the user to the database (the config file)
    config['users']['players'].append(user)

    # Save the changes to the config file
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4, sort_keys=True, separators=(',', ': '))

    # Send a message to the user
    await inter.response.send_message(f"{user} has been registered!")

### /UNREGISTER COMMAND ###
# Command to unregister a user from the bot
# Usage: /unregister <user>
# Parameters: user <str> - The user to unregister
@tree.command(
    name = "unregister",
    description = "Remove a user from the bot",
    guild = discord.Object(id = config['discord']['guild_id'])
)
@app_commands.describe(user = "The user to unregister")
async def unregister(inter, user: str):
    
    # Check if the user is not registered
    if user not in config['users']['players']:
        await inter.response.send_message("User is not registered!")
        return

    # Remove the user from the database (the config file)
    config['users']['players'].remove(user)

    # Save the changes to the config file
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4, sort_keys=True, separators=(',', ': '))

    # Send a message to the user
    await inter.response.send_message(f"{user} has been unregistered!")

### /REGISTER_MAPPER COMMAND ###
# Command to register a mapper to the bot, so that the bot can track their beatmaps
# Usage: /register_mapper <mapper>
# Parameters: mapper <str> - The mapper to register
@tree.command(
    name = "register_mapper",
    description = "Add a mapper for the bot to track",
    guild = discord.Object(id = config['discord']['guild_id'])
)
@app_commands.describe(mapper = "The mapper to register")
async def register_mapper(inter, mapper: str):
    
    # Get the mapper
    current_mapper = osu_client.get_user(mapper)

    # Check if the mapper exists
    if current_mapper is None:
        await inter.response.send_message("Mapper not found!")
        return
    
    # Check if the mapper is already registered
    if mapper in config['users']['mappers']:
        await inter.response.send_message("Mapper is already registered!")
        return
    
    # Add the mapper to the database (the config file)
    config['users']['mappers'].append(mapper)

    # Save the changes to the config file
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4, sort_keys=True, separators=(',', ': '))

    # Send a message to the user
    await inter.response.send_message(f"{mapper} has been registered!")

### /UNREGISTER_MAPPER COMMAND ###
# Command to unregister a mapper from the bot
# Usage: /unregister_mapper <mapper>
# Parameters: mapper <str> - The mapper to unregister
@tree.command(
    name = "unregister_mapper",
    description = "Remove a mapper from the bot",
    guild = discord.Object(id = config['discord']['guild_id'])
)
@app_commands.describe(mapper = "The mapper to unregister")
async def unregister_mapper(inter, mapper: str):
    
    # Check if the mapper is not registered
    if mapper not in config['users']['mappers']:
        await inter.response.send_message("Mapper is not registered!")
        return

    # Remove the mapper from the database (the config file)
    config['users']['mappers'].remove(mapper)

    # Save the changes to the config file
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4, sort_keys=True, separators=(',', ': '))

    # Send a message to the user
    await inter.response.send_message(f"{mapper} has been unregistered!")

### /LIST_USERS COMMAND ###
# Command to list all the registered users
# Usage: /list_users
@tree.command(
    name = "list_users",
    description = "List all registered users",
    guild = discord.Object(id = config['discord']['guild_id'])
)
async def list_users(inter):
    
    # Defer the response
    await inter.response.defer()

    # Get the list of all registered users
    users = config['users']['players']

    # Send a message to the user
    await inter.followup.send(f"Registered Users: {', '.join(users)}")

### /LIST_MAPPERS COMMAND ###
# Command to list all the registered mappers
# Usage: /list_mappers
@tree.command(
    name = "list_mappers",
    description = "List all registered mappers",
    guild = discord.Object(id = config['discord']['guild_id'])
)
async def list_mappers(inter):
    
    # Defer the response
    await inter.response.defer()

    # Get the list of all registered mappers
    mappers = config['users']['mappers']

    # Send a message to the user
    await inter.followup.send(f"Registered Mappers: {', '.join(mappers)}")

### /LEADERBOARD COMMAND ###
# Command to get the top 10 plays of all registered users
# Usage: /leaderboard
@tree.command(
    name = "leaderboard",
    description = "Get the top 10 plays of all users",
    guild = discord.Object(id = config['discord']['guild_id'])
)
async def leaderboard(inter):

    # Defer the response
    await inter.response.defer()

    ### PART 1: FIND THE TOP 10 PLAYS OF ALL USERS ###

    # Initialize the top plays list
    top_plays = []

    # Loop through all the users
    for user in config['users']['players']:

        # Get the user
        current_user = osu_client.get_user(user)

        # Get the top 10 plays of each user
        user_scores = osu_client.get_user_scores(current_user.id, type = "best", mode = "osu", limit = 10)

        # Check the top_plays list is empty
        if len(top_plays) == 0:

            # If this is the first user, set the top plays to their top plays
            top_plays = user_scores
        else:

            # Otherwise, check if the user's top plays are better than the current top plays
            for score in user_scores:

                # Check if the score is better than the current top 10
                if score.pp > top_plays[-1].pp:

                    # Add the score to the top plays list
                    top_plays.append(score)

                    # Sort the top plays list by pp
                    top_plays.sort(key = lambda x: x.pp, reverse = True)

                    # Remove the last score in the list
                    top_plays.pop()
                else:

                    # All other scores will be lower than the current score, so they are not in the top 10
                    break

    ### PART 2: CREATE THE EMBED MESSAGE ###

    # Get all the beatmaps of the user_scores
    user_beatmaps = osu_client.get_beatmaps([score.beatmap_id for score in top_plays])

    # Get the max combos of the beatmaps
    beatmap_max_combos = {beatmap.id: beatmap.max_combo for beatmap in user_beatmaps}

    # Print a simple embed message
    embed = discord.Embed(
        title = f"**Top 10 Plays in the Server**",
        color = 0x158ddc,
        timestamp = datetime.datetime.now()
    )

    # Loop through the top plays list
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

# Run the bot
client.run(config['discord']['token'])