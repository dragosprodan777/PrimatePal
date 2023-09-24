from disnake.ext import commands
import os
import openai

OPENAI_API_KEY = os.environ.get("OPENAI_TOKEN")

# Initialize the OpenAI API client
openai.api_key = OPENAI_API_KEY

COG_COMMAND_COOLDOWN = commands.cooldown(1, 5, commands.BucketType.user)


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
            response = openai.Completion.create(
                model="text-davinci-003",  # You can choose a different engine if desired
                prompt=question,
                max_tokens=100,  # Adjust the response length as needed
                n=1,
                stop=None,
                temperature=1
            )
            print("Received 'chatgpt' command in gpt/cog.py")
        # Extract the generated response from ChatGPT
            answer = response.choices[0].text.strip()

            # Send the response back to the user
            await ctx.send(answer)
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")


def setup(bot):
    bot.add_cog(Cog(bot))
