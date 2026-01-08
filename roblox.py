import aiohttp
from config import ROBLOX_GROUP_ID

async def get_user_id(username: str):
    url = "https://users.roblox.com/v1/usernames/users"
    payload = {
        "usernames": [username],
        "excludeBannedUsers": True
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            data = await response.json()
            if not data["data"]:
                return None
            return data["data"][0]["id"]

async def get_rank(user_id: int):
    url = f"https://groups.roblox.com/v2/users/{user_id}/groups/roles"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            for group in data["data"]:
                if group["group"]["id"] == ROBLOX_GROUP_ID:
                    return group["role"]
    return None
