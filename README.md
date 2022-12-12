# Template-Python-DiscordBot

Discord bot supporting slash commands!

# Running the bot

Create a `.env` file with the following content.

```env
# Discord
DISCORD_BOT_TOKEN=
DISCORD_APPLICATION_ID=
```

Install dependencies
```bash
python -m pip install -r ./requirements.txt
```

Run the bot.
```bash
python ./src/main.py
```

One manual action needs to be done to update the slash commands. As the owner, send a private message with `!sync` to the bot.

## With Docker

```bash
docker-compose build
docker-compose --env-file ./.env up
```