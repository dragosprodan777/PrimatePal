# This idea was my frien's, Andrei. Thank you andrei :thumbs_up:
from disnake.ext import commands
import random
import asyncio

COG_COMMAND_COOLDOWN = commands.cooldown(1, 3, commands.BucketType.user)


class HigherLowerGame:
    def __init__(self):
        self.running_game = True
        self.current_number = None
        self.end_game = False
        self.correct_guesses = 0
        self.wrong_guesses = 0
        self.last_activity_time = None  # Keep track of the last activity time
        self.no_game_started_text = "No game in progress. Start a game with `/higherlower`."

    def start_game(self):
        self.current_number = random.randint(0, 100)
        self.end_game = True
        self.last_activity_time = asyncio.get_event_loop().time()  # Record the start time

    @staticmethod
    def next_number():
        return random.randint(0, 100)

    def check_activity_timeout(self):
        # Check if the game has been inactive for 2 minutes
        if self.end_game and asyncio.get_event_loop().time() - self.last_activity_time > 60:  # End game if IDLE
            self.end_game = False
            return True  # Game ended due to inactivity
        return False


class Cog(commands.Cog, name="HigherLower"):
    def __init__(self, bot):
        self.bot = bot
        self.game = HigherLowerGame()

    @commands.slash_command(
        name="higherlower",
        description="Start a game of higher/lower"
    )
    @COG_COMMAND_COOLDOWN
    async def higherlower(self, ctx):
        if not self.game.end_game:
            self.game.start_game()
            await ctx.send(f"Game started! Current number: {self.game.current_number}. Type `/higher` or `/lower`."
                           f" You can also use `/quitgame` to end the game.")
        else:
            await ctx.send(f"You are already in a game. Current number:"
                           f" {self.game.current_number}. Type `/higher` or `/lower`."
                           f" You can also use `/quitgame` to end the game.")

    @commands.slash_command(
        name="higher",
        description="Guess that the next number will be higher"
    )
    @COG_COMMAND_COOLDOWN
    async def higher(self, ctx):
        if self.game.end_game:
            new_number = self.game.next_number()
            if new_number > self.game.current_number:
                self.game.correct_guesses += 1
                await ctx.send(f"Correct! The next number is {new_number}. Score -> Correct:"
                               f" {self.game.correct_guesses}, Wrong: {self.game.wrong_guesses},"
                               f" Type `/higher` or `/lower`.")
            else:
                self.game.wrong_guesses += 1  # Increment wrong guesses
                await ctx.send(f"Wrooooong! The next number is {new_number}! Score -> Correct:"
                               f" {self.game.correct_guesses}, Wrong: {self.game.wrong_guesses},"
                               f" Type `/higher` or `/lower`.")
            self.game.last_activity_time = asyncio.get_event_loop().time()  # Update activity time
            if self.game.check_activity_timeout():
                await ctx.send("Game ended due to inactivity.")

    @commands.slash_command(
        name="lower",
        description="Guess that the next number will be lower"
    )
    @COG_COMMAND_COOLDOWN
    async def lower(self, ctx):
        if self.game.end_game:
            new_number = self.game.next_number()
            if new_number < self.game.current_number:
                self.game.correct_guesses += 1
                await ctx.send(f"Correct! The next number is {new_number}. Score -> Correct:"
                               f" {self.game.correct_guesses}, Wrong: {self.game.wrong_guesses},"
                               f" Type `/higher` or `/lower`.")
            else:
                self.game.wrong_guesses += 1
                await ctx.send(f"Wrooooong! The next number is {new_number}! Score -> Correct:"
                               f" {self.game.correct_guesses}, Wrong: {self.game.wrong_guesses},"
                               f" Type `/higher` or `/lower`.")
        self.game.last_activity_time = asyncio.get_event_loop().time()  # Update activity time
        if self.game.check_activity_timeout():
            await ctx.send("Game ended due to inactivity.")

    @commands.slash_command(
        name="quitgame",
        description="Quit the current game"
    )
    @COG_COMMAND_COOLDOWN
    async def quitgame(self, ctx):
        if self.game.end_game and self.game.running_game is True:
            self.game.end_game = True
            await ctx.send("You ended the game.")
        else:
            await ctx.send(self.game.no_game_started_text)


def setup(bot):
    bot.add_cog(Cog(bot))
