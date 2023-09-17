from discord.ext import commands
import tracemalloc
import discord
import os

tracemalloc.start()
BOT_TOKEN = os.environ.get("PRIMATE_PAL_TKN")
MIERCURI_ID = 334750929637343232
BOT_COMMANDS_ID = 787686148889509918

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


@bot.event
async def on_ready():
    print("I am ready!")
    channel = bot.get_channel(BOT_COMMANDS_ID)
    await channel.send("Your Pal is back online!")

    for folder in os.listdir("modules"):
        if os.path.exists(os.path.join("modules", folder, "cog.py")):
            try:
                await bot.load_extension(f"modules.{folder}.cog")
            except Exception as e:
                print(f"Failed to load extension 'modules.{folder}.cog': {e}")


bot.run(BOT_TOKEN)
