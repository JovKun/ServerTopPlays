# Import the necessary libraries
from datetime import datetime

# discord.py
import discord

# Repositories
from db.database import Session
import db.repositories.players as player_repo
import db.repositories.mappers as mapper_repo
import db.repositories.last_checked as last_checked_repo

### /check_top_plays ###
async def check_top_plays(discord_client, osu_client, discord_announcement_channel_id):

    print("Checking top plays...")

    # Get the last checked time and all players from the database
    async with Session() as session:
        last_checked_time = await last_checked_repo.get_last_checked_time(session)
        last_checked_time = datetime.fromisoformat(last_checked_time)  # Convert to datetime object
        players = await player_repo.get_all_players(session)

    # If there are no players in the database, log a message and return
    if not players:
        print("No players found in the database.")
        return

    # Get the top 10 plays of each player since the last checked time
    for player in players:

        # Get the user
        user = await osu_client.get_user(player.osu_id, mode = "osu")

        # If the osu! username has changed, update the username in the database
        if user.username != player.username:
            async with Session() as session:
                await player_repo.update_player_in_db(session, player.osu_id, user.username)
                print(f"Updated username for osu_id {player.osu_id} from {player.username} to {user.username}")

        # Debugging: Log the player's username and the last checked time
        print(f"Checking top plays for player: {user.username} (osu_id: {player.osu_id}) since {last_checked_time}")

        # Get the top 10 plays of the user
        top_plays = await osu_client.get_user_scores(user.id, mode = "osu", type = "best", limit = 10)

        # Loop through the top plays
        for ind, top_play in enumerate(top_plays):

            # Get the time the play was set
            play_set_time = top_play.ended_at

            # Check if the play was set from last checked time to now
            if play_set_time.timestamp() > last_checked_time.timestamp():

                # Print a simple embed message
                embed = discord.Embed(
                    title = f"**{user.username} just set a new top play! ({round(top_play.pp, 2)}pp)**",
                    description = f"{user.statistics.pp}pp (#{user.statistics.global_rank} {user.country_code}#{user.statistics.country_rank})",
                    color = 0x158ddc,
                    url = f"https://osu.ppy.sh/users/{user.id}",
                    timestamp = datetime.now()
                )

                # Set the thumbnail of the embed
                embed.set_thumbnail(url = user.avatar_url)

                # Set the values of each data
                user_pp = round(top_play.pp, 2)
                user_accuracy = round(top_play.accuracy * 100, 2)
                
                # ex. current_user.mods = [LazerMod(mod = "HR", settings = None), LazerMod(mod = "DT", settings = None)]
                user_mods = "".join([lazermod.mod.value for lazermod in top_play.mods])
                user_mods = user_mods if user_mods != "" else "NM"

                # ex. current_user.rank = ScoreRank.SILVER_S
                user_rank = top_play.rank.value

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
                star_rate = round(top_play.beatmap.difficulty_rating, 2)

                # Get the max combo of the beatmap
                user_beatmap = await osu_client.get_beatmap(top_play.beatmap_id)
                beatmap_max_combo = user_beatmap.max_combo

                # Get the miss count of the score
                count_miss = "" if top_play.statistics.miss is None else str(top_play.statistics.miss) + "<:miss_nn:1330340826492047481>"

                # Add the field to the embed
                embed.add_field(
                    name="__Personal Best #" + str(ind + 1) + "__",
                    value=f"**[{top_play.beatmapset.title} [{top_play.beatmap.version}]]({top_play.beatmap.url})** [{star_rate}★]\n{user_rank} **{user_pp}pp** ({user_accuracy}%) [**{top_play.max_combo}x**/{beatmap_max_combo}x] {count_miss} \n+**{user_mods}** <t:{int(top_play.ended_at.timestamp())}:R>\n",
                    inline=False
                )

                # Add another field to show the link to the play
                embed.add_field(
                    name="\u200B", # Invisible name for spacing
                    value=f"[Link to Score](https://osu.ppy.sh/scores/{top_play.id})",
                )

                # Add thumbnail to show the beatmap background
                embed.set_image(url = f"https://assets.ppy.sh/beatmaps/{top_play.beatmapset.id}/covers/card.jpg")

                # Send the embed message to the specified channel
                channel = discord_client.get_channel(discord_announcement_channel_id)
                await channel.send(embed = embed)

    print("Finished checking top plays...")

### /check_new_beatmaps ###
async def check_new_beatmaps(discord_client, osu_client, discord_beatmap_channel_id):

    print("Checking new beatmaps...")

    # Get the last checked time and all mappers from the database
    async with Session() as session:
        last_checked_time = await last_checked_repo.get_last_checked_time(session)
        last_checked_time = datetime.fromisoformat(last_checked_time)  # Convert to datetime object
        mappers = await mapper_repo.get_all_mappers(session)

    # If there are no mappers in the database, log a message and return
    if not mappers:
        print("No mappers found in the database.")
        return

    # Get the new beatmaps of each mapper since the last checked time
    for mapper in mappers:

        # Get the user
        user = await osu_client.get_user(mapper.osu_id, mode = "osu")

        # If the osu! username has changed, update the username in the database
        if user.username != mapper.username:
            async with Session() as session:
                await mapper_repo.update_mapper_in_db(session, mapper.osu_id, user.username)
                print(f"Updated username for osu_id {mapper.osu_id} from {mapper.username} to {user.username}")

        # Debugging: Log the mapper's username and the last checked time
        print(f"Checking new beatmaps for mapper: {user.username} (osu_id: {mapper.osu_id}) since {last_checked_time}")

        # Get the beatmaps of the user
        beatmaps = await osu_client.get_user_beatmaps(user.id, type = "pending", limit = 3)

        # Loop through the beatmaps
        for beatmap in beatmaps:

            # Get the time the beatmap was set
            beatmap_set_time = beatmap.last_updated

            # Check if the beatmap was set from last checked time to now
            if beatmap_set_time.timestamp() > last_checked_time.timestamp():

                # Get the beatmap status
                beatmap_status = ""

                if beatmap.status == -1:
                    beatmap_status = "WIP"
                elif beatmap.status == 0:
                    beatmap_status = "Pending"

                # If the beatmap submission date is before the last checked time, break the loop (means that the beatmap was updated and not submitted)
                if beatmap.submitted_at.timestamp() < last_checked_time.timestamp():
                    break

                # Print a simple embed message
                embed = discord.Embed(
                    title = f"**{user.username} just submitted a new beatmap!**",
                    description = f"**[{beatmap.title}](https://osu.ppy.sh/beatmapsets/{beatmap.id})**\nStatus: {beatmap_status}\nHypes: {beatmap.hype.current}/5\n{beatmap.favourite_count} :heart: {beatmap.play_count} :arrow_forward:",
                    color = 0x158ddc,
                    timestamp = datetime.now()
                )

                # Get the list of all the difficulties
                difficulties = beatmap.beatmaps

                # Sort the difficulties by star rating
                difficulties.sort(key=lambda x: x.difficulty_rating, reverse=True)

                # Add the difficulties to the embed
                for difficulty in difficulties:
                    embed.add_field(
                        name=f"**{difficulty.version}**\n{difficulty.difficulty_rating:.2f}★",
                        value="\u200B", # Invisible name for spacing
                        inline=True
                    )

                # Set the thumbnail of the embed to the mapper's avatar
                embed.set_thumbnail(url = user.avatar_url)

                # Add thumbnail to show the beatmap background
                embed.set_image(url = f"https://assets.ppy.sh/beatmaps/{beatmap.id}/covers/card.jpg")

                # Send the embed message to the specified channel
                channel = discord_client.get_channel(discord_beatmap_channel_id)
                await channel.send(embed = embed)

    print("Finished checking new beatmaps...")