from disnake.ext import commands
from disnake.ui import View, Button, button
from disnake import ButtonStyle
import random
import asyncio
import sqlite3

COG_COMMAND_COOLDOWN = commands.cooldown(1, 2, commands.BucketType.user)


class HigherLowerGame:
    def __init__(self):
        self.current_number = None
        self.game_is_running = False
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
                discord_id TEXT PRIMARY KEY,
                correct_guesses INTEGER,
                wrong_guesses INTEGER
            )
        ''')
        self.conn.commit()

    def add_correct_guess(self, discord_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_scores (discord_id, correct_guesses, wrong_guesses)
            VALUES (?, (SELECT correct_guesses FROM user_scores WHERE discord_id = ?) + 1,
             (SELECT wrong_guesses FROM user_scores WHERE discord_id = ?))
        ''', (discord_id, discord_id, discord_id))
        self.conn.commit()

    def add_wrong_guess(self, discord_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_scores (discord_id, correct_guesses, wrong_guesses)
            VALUES (?, (SELECT correct_guesses FROM user_scores WHERE discord_id = ?),
             (SELECT wrong_guesses FROM user_scores WHERE discord_id = ?) + 1)
        ''', (discord_id, discord_id, discord_id))
        self.conn.commit()

    def load_user_scores(self, discord_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT correct_guesses, wrong_guesses FROM user_scores WHERE discord_id = ?', (discord_id,))
        row = cursor.fetchone()
        if row:
            correct_guesses, wrong_guesses = row
        else:
            # If user doesn't exist, create a new row with 0 correct and wrong guesses
            cursor.execute('INSERT INTO user_scores (discord_id, correct_guesses, wrong_guesses) VALUES (?, ?, ?)',
                           (discord_id, 0, 0))
            self.conn.commit()
            correct_guesses, wrong_guesses = 0, 0
        return correct_guesses, wrong_guesses

    def close_connection(self):
        self.conn.close()

    def start_game(self):
        self.current_number = random.randint(0, 100)
        self.game_is_running = True
        self.last_activity_time = asyncio.get_event_loop().time()  # Record the start time for IDLE timer

    @staticmethod
    def next_number():
        return random.randint(0, 100)

    async def check_activity_timeout(self):
        current_time = asyncio.get_event_loop().time()
        if self.game_is_running is True and current_time - self.last_activity_time > 10:
            print("Game ended due to inactivity.")
            self.game_is_running = False
            return True  # Game ended due to inactivity
        print("Game is still active.")
        return False

    async def higher(self, interaction):
        if self.game_is_running:
            new_number = self.next_number()

            print(f"Pressed 'Higher' button in higherlower/cog.py: evaluate"
                  f" {new_number} higher than {self.current_number}"
                  f" from: {interaction.author.name}")

            correct_guesses, wrong_guesses = self.load_user_scores(interaction.author.id)

            if new_number == self.current_number:
                correct_guesses, _ = self.load_user_scores(interaction.author.id)
                message = (f"Hmmm, looks like a draw! The next number is {new_number}."
                           f" Score: Correct: {correct_guesses}, Wrong: {wrong_guesses}")

                await self.update_prompt(interaction, message)
                print("Result -- DRAW")
            else:
                if new_number > self.current_number:
                    self.add_correct_guess(interaction.author.id)
                    correct_guesses, _ = self.load_user_scores(interaction.author.id)
                    message = (f"Correct! The next number is {new_number}."
                               f" Score: Correct: {correct_guesses}, Wrong: {wrong_guesses}")

                    await self.update_prompt(interaction, message)
                    print("Result -- CORRECT")
                else:
                    self.add_wrong_guess(interaction.author.id)
                    _, wrong_guesses = self.load_user_scores(interaction.author.id)
                    message = (f"Wrooooong! The next number is {new_number}!"
                               f" Score: Correct: {correct_guesses}, Wrong: {wrong_guesses}")
                    await self.update_prompt(interaction, message)
                    print("Result -- WRONG")

                self.current_number = new_number  # Update the current number for the next iteration
                self.last_activity_time = asyncio.get_event_loop().time()  # Update activity time
                if await self.check_activity_timeout():
                    await self.update_prompt(interaction, self.inactivity_message)
                    view = interaction.message.view
                    await view.disable_buttons(interaction)

    async def lower(self, interaction):
        if self.game_is_running:
            new_number = self.next_number()

            print(f"Pressed 'Lower' button in higherlower/cog.py: evaluate"
                  f" {new_number} lower than {self.current_number}"
                  f" from: {interaction.author.name}")

            correct_guesses, wrong_guesses = self.load_user_scores(interaction.author.id)

            if new_number == self.current_number:
                correct_guesses, _ = self.load_user_scores(interaction.author.id)
                message = (f"Hmmm, looks like a draw! The next number is {new_number}."
                           f" Score: Correct: {correct_guesses}, Wrong: {wrong_guesses}")

                await self.update_prompt(interaction, message)
            else:
                if new_number < self.current_number:
                    self.add_correct_guess(interaction.author.id)
                    correct_guesses, _ = self.load_user_scores(interaction.author.id)
                    message = (f"Correct! The next number is {new_number}."
                               f" Score: Correct: {correct_guesses}, Wrong: {wrong_guesses}")

                    await self.update_prompt(interaction, message)
                    print("Result -- CORRECT")
                else:
                    self.add_wrong_guess(interaction.author.id)
                    _, wrong_guesses = self.load_user_scores(interaction.author.id)
                    message = (f"Wrooooong! The next number is {new_number}!"
                               f" Score: Correct: {correct_guesses}, Wrong: {wrong_guesses}")
                    await self.update_prompt(interaction, message)
                    print("Result -- WRONG")

                self.current_number = new_number  # Update the current number for the next iteration
                self.last_activity_time = asyncio.get_event_loop().time()  # Update activity time
                if await self.check_activity_timeout():
                    await self.update_prompt(interaction, self.inactivity_message)
                    view = interaction.message.view
                    await view.disable_buttons(interaction)

    async def quitgame(self, interaction):
        if self.game_is_running is True:
            self.game_is_running = False
            print("Pressed 'Quit Game' button in higherlower/cog.py")
            message = "You ended the game."
            await self.update_prompt(interaction, message)
            return True
        else:
            return False


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
    async def quitgame_call(self, button_signature, interaction):
        await self.game.quitgame(interaction)
        self.game.game_is_running = False
        await self.disable_buttons()
        await interaction.edit_original_message(view=self)  # Edit the original message to remove all buttons
        _ = button_signature

    async def disable_buttons(self):
        buttons_to_remove = []
        for child in self.children:
            if isinstance(child, Button):
                buttons_to_remove.append(child)

        for btn in buttons_to_remove:
            self.remove_item(btn)


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

        if not self.game.game_is_running:
            self.game.start_game()
            view = HigherLowerView(self.game)
            await ctx.send(f"Game started! Current number: {self.game.current_number}", view=view)
        else:
            await ctx.send(f"You are already in a game. Current number:"
                           f" {self.game.current_number}.")


def setup(bot):
    bot.add_cog(Cog(bot))
