|      **Commands**      |      **What it does**      |
| :----------------: | :--------------------: |
|      /register_player [user]| Registers a player to be tracked |
|      /unregister_player [user]| Removes a player from tracking |
|      /register_mapper [user]| Registers a mapper to be tracked |
|      /unregister_mapper [user]| Removes a mapper from tracking |
|      /list_players | Prints all the players registered |
|      /list_mappers | Prints all the mappers registered |
|      /top [user]   | Prints the top 10 plays of a user |
|      /leaderboard  | Prints the top 10 plays of the server |


|      **Background Tasks**      |      **What it does**      |
| :----------------: | :--------------------: |
|      `check_top_plays` | Checks for new top plays from registered players |
|      `check_new_beatmaps` | Checks for new maps from registered mappers |


|      **Directory / File**         |      **What it does**      |
| :----------------: | :--------------------: |
|      `api/`        | FastAPI application and REST API endpoints |
|      `bot/`        | Discord bot commands and startup logic |
|      `db/`         | PostgreSQL connection, SQLAlchemy models, and database repositories |
|      `tests/`      | Automated tests for the application |
|      `.env`        | Stores environment variables and sensitive information (hidden) |
|      `alembic.ini` | Alembic configuration for database migrations |
|      `alembic/`    | Database migration scripts |
|      `README.md`   | Project documentation |
|      `changelog.md`| Logs project changes and versions |


## How the bot works

The bot periodically checks the osu! API for activity from registered players
and mappers. These checks run every 2 minutes in the background while the bot
remains available for Discord commands.

### Top plays

The `check_top_plays` background task retrieves the top 10 plays of each
registered player through the osu! API. Each play is compared against the
server's `last_checked` timestamp. If a new play is detected, the bot creates
a Discord embed containing relevant information about the play and sends it
to the server's announcement channel.

### New beatmaps

The `check_new_beatmaps` background task retrieves beatmaps associated with
registered mappers. It checks maps with a `Pending` or `WIP` status and
compares their upload or last-update timestamps against `last_checked`.
Newly detected maps are then announced in the server's announcement channel.

### Backend

The bot uses a PostgreSQL database to store registered players, registered
mappers, and the timestamp of the most recent check. SQLAlchemy provides the
database interface, while Alembic manages database schema migrations.

The project also includes a FastAPI backend, providing a REST API for
interacting with the application's data independently of the Discord bot.

## Architecture

ServerTopPlays combines a Discord bot with a FastAPI backend and PostgreSQL
database. The Discord bot handles user interaction and automated announcements,
while the backend and database provide persistent data storage and a
separation between application logic and Discord-specific functionality.

Background tasks allow the bot to periodically monitor osu! activity while
remaining responsive to Discord commands.