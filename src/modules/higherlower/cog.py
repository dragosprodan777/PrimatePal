from disnake.ext import commands
from disnake.ui import View, button
from disnake import ButtonStyle
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
        self.prompt_message = None

        self.conn = sqlite3.connect("modules/higherlower/higherlower.db")  # Create a table for scores in the module
        self.create_scores_table()

    @staticmethod
    async def update_prompt(interaction, new_content):
        await interaction.response.edit_message(content=new_content)

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

    async def higher(self, interaction):
        if self.end_game:
            new_number = self.next_number()

            print(f"Pressed 'Higher' button in higherlower/cog.py: evaluate"
                  f" {new_number} higher than {self.current_number}"
                  f" from: {interaction.author.name}")

            correct_guesses, wrong_guesses = self.load_user_scores(interaction.author.name)

            if new_number == self.current_number:
                correct_guesses, _ = self.load_user_scores(interaction.author.name)
                message = (f"Hmmm, looks like a draw! The next number is {new_number}."
                           f" Score: Correct: {correct_guesses}, Wrong: {wrong_guesses}")

                await self.update_prompt(interaction, message)
                print("Result -- DRAW")
            else:
                if new_number > self.current_number:
                    self.add_correct_guess(interaction.author.name)
                    correct_guesses, _ = self.load_user_scores(interaction.author.name)
                    message = (f"Correct! The next number is {new_number}."
                               f" Score: Correct: {correct_guesses}, Wrong: {wrong_guesses}")

                    await self.update_prompt(interaction, message)
                    print("Result -- CORRECT")
                else:
                    self.add_wrong_guess(interaction.author.name)
                    _, wrong_guesses = self.load_user_scores(interaction.author.name)
                    message = (f"Wrooooong! The next number is {new_number}!"
                               f" Score: Correct: {correct_guesses}, Wrong: {wrong_guesses}")
                    await self.update_prompt(interaction, message)
                    print("Result -- WRONG")

                self.current_number = new_number  # Update the current number for the next iteration
                self.last_activity_time = asyncio.get_event_loop().time()  # Update activity time
                if self.check_activity_timeout():
                    await interaction.send(self.inactivity_message)

    async def lower(self, interaction):
        if self.end_game:
            new_number = self.next_number()

            print(f"Pressed 'Lower' button in higherlower/cog.py: evaluate"
                  f" {new_number} lower than {self.current_number}"
                  f" from: {interaction.author.name}")

            correct_guesses, wrong_guesses = self.load_user_scores(interaction.author.name)

            if new_number == self.current_number:
                correct_guesses, _ = self.load_user_scores(interaction.author.name)
                message = (f"Hmmm, looks like a draw! The next number is {new_number}."
                           f" Score: Correct: {correct_guesses}, Wrong: {wrong_guesses}")

                await self.update_prompt(interaction, message)
            else:
                if new_number < self.current_number:
                    self.add_correct_guess(interaction.author.name)
                    correct_guesses, _ = self.load_user_scores(interaction.author.name)
                    message = (f"Correct! The next number is {new_number}."
                               f" Score: Correct: {correct_guesses}, Wrong: {wrong_guesses}")

                    await self.update_prompt(interaction, message)
                    print("Result -- CORRECT")
                else:
                    self.add_wrong_guess(interaction.author.name)
                    _, wrong_guesses = self.load_user_scores(interaction.author.name)
                    message = (f"Wrooooong! The next number is {new_number}!"
                               f" Score: Correct: {correct_guesses}, Wrong: {wrong_guesses}")
                    await self.update_prompt(interaction, message)
                    print("Result -- WRONG")

                self.current_number = new_number  # Update the current number for the next iteration
                self.last_activity_time = asyncio.get_event_loop().time()  # Update activity time
                if self.check_activity_timeout():
                    await interaction.send(self.inactivity_message)

    async def quitgame(self, interaction):
        if self.end_game and self.running_game is True:
            self.end_game = True
            print("Pressed 'Quit Game' button in higherlower/cog.py")
            await interaction.send("You ended the game.")
        else:
            await interaction.send(self.no_game_started_text)


class HigherLowerView(View):
    def __init__(self, game):
        super().__init__()
        self.game = game

    @button(label="Higher", style=ButtonStyle.green, custom_id="higher")
    async def higher_call(self, button_signature, interaction):
        await self.game.higher(interaction)
        _ = button_signature

    @button(label="Lower", style=ButtonStyle.red, custom_id="lower")
    async def lower_call(self, button_signature, interaction):
        await self.game.lower(interaction)
        _ = button_signature

    @button(label="Quit Game", style=ButtonStyle.gray, custom_id="quitgame")
    async def quitgame_call(self, button_signature,  interaction):
        await self.game.quitgame(interaction)
        _ = button_signature


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
        print(f"Received 'higherlower' command from {ctx.author.name}")

        if not self.game.end_game:
            self.game.start_game()
            view = HigherLowerView(self.game)
            self.prompt_message = await ctx.send(f"Game started! Current number: {self.game.current_number}", view=view)
        else:
            await ctx.send(f"You are already in a game. Current number:"
                           f" {self.game.current_number}.")


def setup(bot):
    bot.add_cog(Cog(bot))
