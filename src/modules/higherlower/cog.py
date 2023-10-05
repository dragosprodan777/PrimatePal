# This idea was my friend's, Andrei. Thank you, Andrei :thumbs_up:
from disnake.ext import commands
import random
import asyncio
import sqlite3

COG_COMMAND_COOLDOWN = commands.cooldown(1, 2, commands.BucketType.user)


class HigherLowerGame:
    def __init__(self):
        self.running_game = True
        self.current_number = None
        self.end_game = False
        self.inactivity_message = "Game ended due to inactivity."
        self.last_activity_time = None  # Keep track of the last activity time
        self.no_game_started_text = "No game in progress. Start a game with `/higherlower`."

        self.conn = sqlite3.connect("modules/higherlower/higherlower.db")  # Create a table for scores in the module
        self.create_scores_table()

    def create_scores_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_scores (
                username TEXT PRIMARY KEY,
                correct_guesses INTEGER,
                wrong_guesses INTEGER
            )
        ''')
        self.conn.commit()

    def add_correct_guess(self, username):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_scores (username, correct_guesses, wrong_guesses)
            VALUES (?, (SELECT correct_guesses FROM user_scores WHERE username = ?) + 1,
             (SELECT wrong_guesses FROM user_scores WHERE username = ?))
        ''', (username, username, username))
        self.conn.commit()

    def add_wrong_guess(self, username):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_scores (username, correct_guesses, wrong_guesses)
            VALUES (?, (SELECT correct_guesses FROM user_scores WHERE username = ?),
             (SELECT wrong_guesses FROM user_scores WHERE username = ?) + 1)
        ''', (username, username, username))
        self.conn.commit()

    def load_user_scores(self, username):
        cursor = self.conn.cursor()
        cursor.execute('SELECT correct_guesses, wrong_guesses FROM user_scores WHERE username = ?', (username,))
        row = cursor.fetchone()
        if row:
            correct_guesses, wrong_guesses = row
        else:
            # If user doesn't exist, create a new row with 0 correct and wrong guesses
            cursor.execute('INSERT INTO user_scores (username, correct_guesses, wrong_guesses) VALUES (?, ?, ?)',
                           (username, 0, 0))
            self.conn.commit()
            correct_guesses, wrong_guesses = 0, 0
        return correct_guesses, wrong_guesses

    def close_connection(self):
        self.conn.close()

    def start_game(self):
        self.current_number = random.randint(0, 100)
        self.end_game = True
        self.last_activity_time = asyncio.get_event_loop().time()  # Record the start time for IDLE timer

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
        self.game = HigherLowerGame()
        print(f"Received 'higherlower' command in higherlower/cog.py: from {ctx.author.name}")

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

            print(f"Received 'higher' command in higherlower/cog.py: evaluate"
                  f" {new_number} higher than {self.game.current_number}"
                  f" from: {ctx.author.name}")

            correct_guesses, wrong_guesses = self.game.load_user_scores(ctx.author.name)
            self.game.correct_guesses = correct_guesses
            self.game.wrong_guesses = wrong_guesses

            if new_number == self.game.current_number:
                correct_guesses, _ = self.game.load_user_scores(ctx.author.name)
                await ctx.send(f"Hmmm, looks like a draw! The next number is {new_number}. Score -> Correct:"
                               f" {self.game.correct_guesses}, Wrong: {self.game.wrong_guesses},"
                               f" Type `/higher` or `/lower`.")
                print("Result -- DRAW")
            else:
                if new_number > self.game.current_number:
                    self.game.add_correct_guess(ctx.author.name)
                    correct_guesses, _ = self.game.load_user_scores(ctx.author.name)
                    await ctx.send(f"Correct! The next number is {new_number}. Score -> Correct:"
                                   f" {correct_guesses}, Wrong: {self.game.wrong_guesses},"
                                   f" Type `/higher` or `/lower`.")
                    print("Result -- CORRECT")
                else:
                    self.game.add_wrong_guess(ctx.author.name)
                    _, wrong_guesses = self.game.load_user_scores(ctx.author.name)
                    await ctx.send(f"Wrooooong! The next number is {new_number}! Score -> Correct:"
                                   f" {self.game.correct_guesses}, Wrong: {wrong_guesses},"
                                   f" Type `/higher` or `/lower`.")
                    print("Result -- WRONG")

                self.game.current_number = new_number  # Update the current number for the next iteration
                self.game.last_activity_time = asyncio.get_event_loop().time()  # Update activity time
                if self.game.check_activity_timeout():
                    await ctx.send(self.game.inactivity_message)

    @commands.slash_command(
        name="lower",
        description="Guess that the next number will be lower"
    )
    @COG_COMMAND_COOLDOWN
    async def lower(self, ctx):
        if self.game.end_game:
            new_number = self.game.next_number()

            print(f"Received 'lower' command in higherlower/cog.py: evaluate"
                  f" {new_number} lower than {self.game.current_number}"
                  f" from: {ctx.author.name}")

            correct_guesses, wrong_guesses = self.game.load_user_scores(ctx.author.name)
            self.game.correct_guesses = correct_guesses
            self.game.wrong_guesses = wrong_guesses

            if new_number == self.game.current_number:
                await ctx.send(f"Hmm, looks like a draw! The next number is {new_number}. Score -> Correct:"
                               f" {self.game.correct_guesses}, Wrong: {self.game.wrong_guesses},"
                               f" Type `/higher` or `/lower`.")
                print("Result -- DRAW")
            else:
                if new_number < self.game.current_number:
                    self.game.add_correct_guess(ctx.author.name)
                    correct_guesses, _ = self.game.load_user_scores(ctx.author.name)
                    await ctx.send(f"Correct! The next number is {new_number}. Score -> Correct:"
                                   f" {correct_guesses}, Wrong: {self.game.wrong_guesses},"
                                   f" Type `/higher` or `/lower`.")
                    print("Result -- CORRECT")
                else:
                    self.game.add_wrong_guess(ctx.author.name)
                    _, wrong_guesses = self.game.load_user_scores(ctx.author.name)
                    await ctx.send(f"Wrooooong! The next number is {new_number}! Score -> Correct:"
                                   f" {self.game.correct_guesses}, Wrong: {wrong_guesses},"
                                   f" Type `/higher` or `/lower`.")
                    print("Result -- WRONG")

                self.game.current_number = new_number  # Update the current number for the next iteration
                self.game.last_activity_time = asyncio.get_event_loop().time()  # Update activity time
                if self.game.check_activity_timeout():
                    await ctx.send(self.game.inactivity_message)

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
