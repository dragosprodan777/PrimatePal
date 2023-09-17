from discord.ext import commands


class Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx):
        print("Received 'hello' command in cog.py")
        await ctx.send("Hello, dear friend!")

    @commands.command()
    async def hi(self, ctx):
        print("Received 'hi' command in cog.py")
        await ctx.send("Hi!")


async def setup(bot):
    await bot.add_cog(Cog(bot))
