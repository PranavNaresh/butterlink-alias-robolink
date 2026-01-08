import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
ROBLOX_GROUP_ID = int(os.getenv("ROBLOX_GROUP_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
