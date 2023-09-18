import discord
from discord.ext import commands
from gtts import gTTS
import asyncio

COG_COMMAND_COOLDOWN = commands.cooldown(1, 5, commands.BucketType.user)


class Cog(commands.Cog, name="sayBack"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @COG_COMMAND_COOLDOWN
    async def tts(self, ctx, *, text_to_say):
        print(f"Received 'sayBack' command in tts/cog.py: {text_to_say}")

        # Check if the user is in a voice channel
        if ctx.author.voice is None:
            await ctx.send("You are not in a voice channel.")
            return

        # Get the user's voice channel
        voice_channel = ctx.author.voice.channel

        # Join the voice channel
        voice_client = await voice_channel.connect()

        # Convert text to speech
        tts = gTTS(text=text_to_say, lang='en')

        # Save the TTS as an audio file
        tts.save('text_to_speech.mp3')

        # Play the audio file in the voice channel
        voice_client.play(discord.FFmpegPCMAudio('text_to_speech.mp3'))

        # Wait for the audio to finish playing
        while voice_client.is_playing():
            await asyncio.sleep(1)

        # Disconnect from the voice channel
        await voice_client.disconnect()

        # Delete the temporary audio file
        import os
        os.remove('text_to_speech.mp3')


async def setup(bot):
    await bot.add_cog(Cog(bot))
