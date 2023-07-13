from discord.ext import commands
import discord
import os

BOT_TOKEN = os.environ.get("PRIMATE_PAL_TKN")
MIERCURI_ID = 334750929637343232
BOT_COMMANDS_ID = 787686148889509918

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


@bot.event
async def on_ready():
    print("I am ready!")

bot.run(BOT_TOKEN)
