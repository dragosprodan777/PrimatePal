from disnake.ext import commands


class Cog(commands.Cog, name="Leave"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="leave",
        description="Disconnect the bot from the voice channel"
    )
    async def leave(self, ctx):
        print("Received 'leave' command in leave/cog.py from", ctx.author.name)

        # Check if the user who issued the command is in a voice channel
        if ctx.author.voice:
            voice_state = ctx.author.voice
            voice_channel = voice_state.channel

            # Check if the bot is in the same voice channel as the user
            if ctx.guild.voice_client and ctx.guild.voice_client.channel == voice_channel:
                # Disconnect the bot from the voice channel
                await ctx.guild.voice_client.disconnect()
                await ctx.send("I have left the voice channel.")
            else:
                await ctx.send("I'm not in the same voice channel as you.")
        else:
            await ctx.send("You are not in a voice channel.")


def setup(bot):
    bot.add_cog(Cog(bot))
