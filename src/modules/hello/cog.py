from disnake.ext import commands


class Cog(commands.Cog, name="Hello"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="hello",
        description="Say hello to the bot"
    )
    async def hello(self, ctx):
        print("Received 'hello' command in hello/cog.py")
        await ctx.send("Hello, dear friend!")


def setup(bot):
    bot.add_cog(Cog(bot))
