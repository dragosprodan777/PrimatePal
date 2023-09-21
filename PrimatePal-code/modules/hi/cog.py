from disnake.ext import commands


class Cog(commands.Cog, name="Hi"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="hi",
        description="Say hi to the bot"
    )
    async def hello(self, ctx):
        print("Received 'hi' command in hi/cog.py")
        await ctx.send("Hi")


def setup(bot):
    bot.add_cog(Cog(bot))
