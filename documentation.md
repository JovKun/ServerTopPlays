|      **Commands**      |      **What it does**      |
| :----------------: | :--------------------: |
|      /register [user]| Registers a user to be tracked by the bot |
|      /unregister [user]| Unregisters a user to be tracked by the bot |
|      /register_mapper [mapper]| Registers a mapper to be tracked by the bot |
|      /unregister_mapper [mapper]| Unregisters a mapper to be tracked by the bot |
|      /register_mapper [mapper]| Registers a mapper to be tracked by the bot |
|      /list_users   | Prints all the users registered |
|      /list_mappers | Prints all the mappers registered |
|      /top [user]   | Prints the top 10 plays of a user |
|      /leaderboard  | Prints the top 10 plays of the server |


|      **Listeners**      |      **What it does**      |
| :----------------: | :--------------------: |
|      /check_top_plays | Listens for top plays submitted by registered users |
|      /check_new_beatmaps | Listens for new beatmaps submitted or updated by registered mappers |


|      **Files**         |      **What it does**      |
| :----------------: | :--------------------: |
|      bot.py        | Main script for the bot |
|      config.json   | Stores data and important information (hidden) |
|      README.md     | This file |
|      changelog.md  | Markdown file for logging changes and versions |


## How the bot works
Using internal functions, such as `/check_top_plays` and `/check_new_beatmaps`, each running once every 2 minutes, checks new top plays of those who registered and new maps created by mappers.
This works by using the osu!API to fetch the top 10 plays of every user, then checking which one has been made after the `last_checked` internal UNIX timestamp.
If it does find a top play, then it uses the Discord bot API for Python to create an embed listing all relevant information about the play, then prints it to an announcement channel on a specific server.
The same thing is done for checking new maps from mappers, where the function fetches all maps from a mapper that has the status `Pending` or `WIP` (since those are the only two possible statuses after uploading a new beatmap), then checking the date of upload/update against `last_checked`.

The only problem with Discord bots is that they are really only made to do one of the tasks at a time: 1) have an active listener (aka `check_top_plays`) or 2) do basic commands and monitor in-app chats (like MEE6).
With this bot, I was attempting to find a way to include both, which required some weird setup with coroutines and parallel processing.
