import disnake
from dotenv import load_dotenv
import datetime
from disnake.ext import commands
import os

load_dotenv()
BOT_TOKEN = os.environ.get("PRIMATE_PAL_TOKEN")

ONLINE_CHECK_PRIMATE_PAL_SV = 1160152031361777684

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
    channel = bot.get_channel(ONLINE_CHECK_PRIMATE_PAL_SV)
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    await channel.send(f"Your Pal is back online at {now}!")

bot.run(BOT_TOKEN)
