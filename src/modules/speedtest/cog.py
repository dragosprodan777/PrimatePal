from disnake.ext import commands
import speedtest


class SpeedTestCog(commands.Cog, name="SpeedTest"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="speedtest",
        description="Run an internet speed test"
    )
    async def run_speedtest(self, ctx):
        print("Received 'speedtest' command from", ctx.author.name)
        await ctx.send(f"Calculating server speed, {ctx.author.mention}. It will take a minute. Stay tight!")

        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        upload_speed = st.upload() / 1_000_000

        # Send the speed test results to the author who invoked the command
        await ctx.author.send(f"Download Speed: {download_speed:.2f} Mbps\nUpload Speed: {upload_speed:.2f} Mbps")
        await ctx.send("Speed test results sent to your DMs!")


def setup(bot):
    bot.add_cog(SpeedTestCog(bot))
