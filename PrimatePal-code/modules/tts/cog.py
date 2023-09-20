import discord
from discord.ext import commands
from gtts import gTTS
import asyncio
import os
discord.opus.load_opus("/opt/homebrew/Cellar/opus/1.4/lib/libopus.dylib")

COG_COMMAND_COOLDOWN = commands.cooldown(1, 5, commands.BucketType.user)


class Cog(commands.Cog, name="sayBack"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @COG_COMMAND_COOLDOWN
    async def tts(self, ctx, *, text_to_say):
        print(f"Received 'tts' command in tts/cog.py: {text_to_say}")

        # Check if the text exceeds the character limit
        if len(text_to_say) > 150:
            await ctx.send("The text exceeds the character limit of 150.")
            return

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

        mp3_path = "modules/tts/text_to_speech.mp3"

        # Save the TTS as an audio file with the constant filename
        tts.save(mp3_path)

        # Play the audio file in the voice channel
        voice_client.play(discord.FFmpegPCMAudio(mp3_path))

        # Wait for the audio to finish playing
        while voice_client.is_playing():
            await asyncio.sleep(1)

        # Disconnect from the voice channel
        await voice_client.disconnect()

        # Delete the temporary audio file
        os.remove(mp3_path)


async def setup(bot):
    await bot.add_cog(Cog(bot))
