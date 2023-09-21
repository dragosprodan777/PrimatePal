import disnake
from disnake.ext import commands
import os

BOT_TOKEN = os.environ.get("PRIMATE_PAL_TOKEN")
MIERCURI_ID = 334750929637343232
BOT_COMMANDS_ID = 787686148889509918

bot = commands.Bot(command_prefix='!', intents=disnake.Intents.all())


def load_cogs():
    for folder in os.listdir("modules"):
        cog_path = f"modules.{folder}.cog"
        if os.path.exists(os.path.join("modules", folder, "cog.py")):
            try:
                bot.load_extension(cog_path)
                print(f"Loaded extension '{cog_path}'")
            except Exception as e:
                print(f"Failed to load extension '{cog_path}': {e}")


# Load ALL cogs before running the bot
load_cogs()


@bot.event
async def on_ready():
    print("I am ready!")
    channel = bot.get_channel(BOT_COMMANDS_ID)
    await channel.send("Your Pal is back online!")

bot.run(BOT_TOKEN)
