from discord.ext import commands


class Cog(commands.Cog, name="Leave"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def leave(self, ctx):
        print("Received 'leave' command in disconnect/cog.py")

        # Check if the bot is connected to a voice channel in the same guild as the command
        if ctx.voice_client:
            # Disconnect from the voice channelcd
            await ctx.voice_client.disconnect()
            await ctx.send("I have left the voice channel.")
        else:
            await ctx.send("I'm not in a voice channel.")


async def setup(bot):
    await bot.add_cog(Cog(bot))
