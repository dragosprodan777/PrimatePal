from discord.ext import commands
COG_COMMAND_COOLDOWN = commands.cooldown(1, 5, commands.BucketType.user)


class Cog(commands.Cog, name="Hello"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @COG_COMMAND_COOLDOWN
    async def hello(self, ctx):
        print("Received 'hello' command in hello/cog.py")
        await ctx.send("Hello, dear friend!")


async def setup(bot):
    await bot.add_cog(Cog(bot))
