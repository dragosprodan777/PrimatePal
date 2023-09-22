import disnake
import os
from disnake.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import asyncio

SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_TOKEN")
COG_COMMAND_COOLDOWN = commands.cooldown(1, 5, commands.BucketType.user)


class Cog(commands.Cog, name="play"):
    def __init__(self, bot):
        self.bot = bot
        self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id='de4dc67a2c0b45e0aa8598a287901f77',
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri='http://localhost:3000/auth/discord/callback',
            scope='user-modify-playback-state')
        )

    @commands.slash_command(
        name="play",
        description="Play a track from Spotify (Name or Link)"
    )
    @COG_COMMAND_COOLDOWN
    async def play(self, ctx, *, query):
        # Search for a track on Spotify
        results = self.spotify.search(q=query, limit=1, type='track')

        if not results['tracks']['items']:
            await ctx.send("No tracks found.")
            return

        #        ##track_name = track['name']
        track = results['tracks']['items'][0]
        track_url = track['external_urls']['spotify']

        # Check if the user is in a voice channel
        if ctx.author.voice is None:
            await ctx.send("You are not in a voice channel.")
            return

        # Get the user's voice channel
        voice_channel = ctx.author.voice.channel

        # Join the voice channel
        voice_client = await voice_channel.connect()

        # Play the Spotify track
        voice_client.play(disnake.FFmpegPCMAudio(executable="ffmpeg", source=track_url))

        # Wait for the track to finish
        while voice_client.is_playing():
            await asyncio.sleep(1)

        # Disconnect from the voice channel
        await voice_client.disconnect()


def setup(bot):
    bot.add_cog(Cog(bot))
