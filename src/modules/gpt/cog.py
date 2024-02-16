from disnake.ext import commands
import os
from openai import OpenAI
client = OpenAI()
OpenAI.api_key = os.getenv('OPENAI_API_KEY')


# Initialize the OpenAI API client

COG_COMMAND_COOLDOWN = commands.cooldown(1, 20, commands.BucketType.user)


class Cog(commands.Cog, name="chatgpt"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="chatgpt",
        description="Ask a question to ChatGPT"
    )
    @COG_COMMAND_COOLDOWN
    async def chatgpt(self, ctx, *, question):
        try:
            # Send the user's question to ChatGPT
            response = client.completions.createcompletion = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt="Say this is a test",
            max_tokens=7,
            temperature=0
            )

            print(f"Received 'chatgpt' command in gpt/cog.py: '{question}' from {ctx.author.name}")

        # Extract the generated response from ChatGPT
            answer = response.choices[0].text.strip()

            # Send the response back to the user
            await ctx.send(answer)
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")


def setup(bot):
    bot.add_cog(Cog(bot))