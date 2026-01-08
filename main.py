import discord
import json
from discord.ext import commands, tasks
from discord import app_commands
from config import TOKEN, GUILD_ID, LOG_CHANNEL_ID
from roblox import get_user_id, get_rank

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def load_db():
    with open("database.json", "r") as f:
        return json.load(f)

def save_db(data):
    with open("database.json", "w") as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    auto_resync.start()
    print(f"🧈 Butterlink online as {bot.user}")

@bot.tree.command(name="verify", description="Verify your Roblox account")
@app_commands.describe(username="Your Roblox username")
async def verify(interaction: discord.Interaction, username: str):
    await interaction.response.defer(ephemeral=True)

    user_id = await get_user_id(username)
    if not user_id:
        return await interaction.followup.send("❌ Roblox user not found.")

    role_data = await get_rank(user_id)
    if not role_data:
        return await interaction.followup.send("❌ You are not in the group.")

    db = load_db()
    db[str(interaction.user.id)] = {
        "roblox": username,
        "rank": role_data["rank"]
    }
    save_db(db)

    role = discord.utils.get(interaction.guild.roles, name=role_data["name"])
    if role:
        await interaction.user.add_roles(role)

    try:
        await interaction.user.edit(nick=username)
    except:
        pass

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(
            f"✅ **{interaction.user}** verified as **{username}**"
        )

    await interaction.followup.send("✅ Verification successful!")

@bot.tree.command(name="resync", description="Resync your Roblox roles")
async def resync(interaction: discord.Interaction):
    db = load_db()
    if str(interaction.user.id) not in db:
        return await interaction.response.send_message(
            "❌ You are not verified.", ephemeral=True
        )

    username = db[str(interaction.user.id)]["roblox"]
    user_id = await get_user_id(username)
    role_data = await get_rank(user_id)

    for role in interaction.user.roles:
        if role.name.startswith("Rank"):
            await interaction.user.remove_roles(role)

    new_role = discord.utils.get(
        interaction.guild.roles, name=role_data["name"]
    )
    if new_role:
        await interaction.user.add_roles(new_role)

    await interaction.response.send_message("🔄 Resynced!", ephemeral=True)

@tasks.loop(minutes=30)
async def auto_resync():
    guild = bot.get_guild(GUILD_ID)
    db = load_db()

    for discord_id, data in db.items():
        member = guild.get_member(int(discord_id))
        if not member:
            continue

        user_id = await get_user_id(data["roblox"])
        role_data = await get_rank(user_id)

        for role in member.roles:
            if role.name.startswith("Rank"):
                await member.remove_roles(role)

        new_role = discord.utils.get(guild.roles, name=role_data["name"])
        if new_role:
            await member.add_roles(new_role)

bot.run(TOKEN)
