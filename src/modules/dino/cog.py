from disnake.ext import commands
from disnake.ui import View, Button, button
from disnake import ButtonStyle
import random
import asyncio


class DinoGame:
    def __init__(self, frame_rate):
        self.board_width = 30
        self.board_height = 3
        self.dino_position = [2, 3]  # Fixed Dino position
        self.cacti_positions = self.generate_cacti()
        self.is_jumping = False
        self.jump_counter = 0
        self.frame_rate = frame_rate

    def get_state(self):
        return {
            "board": self.render(),
            "game_over": self.is_game_over()
            }

    def generate_cacti(self):
        # Generate cacti positions with at least 12 spaces between them
        positions = []
        position = random.randint(15, 25)
        while position < self.board_width:
            positions.append(position)
            position += random.randint(12, 20)
        return positions

    def update(self):
        # Move cacti left by one position each frame
        self.cacti_positions = [pos - 1 for pos in self.cacti_positions if pos > 0]

        # Handle jump logic
        if self.is_jumping:
            self.jump_counter += 1
            if self.jump_counter >= 4:  # Reset jump after 4 frames
                self.is_jumping = False
                self.jump_counter = 0

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_counter = 0

    def render(self):
        board = [[' ' for _ in range(self.board_width)] for _ in range(self.board_height)]
        # Place the Dino (adjust position if jumping)
        dino_row = 1 if self.is_jumping and self.jump_counter < 2 else 2
        board[self.dino_position[0]][self.dino_position[1]] = '🦖'

        # Place the cacti
        for pos in self.cacti_positions:
            board[2][pos] = '🌵'

        # Create a border around the game area
        border_row = '_' * self.board_width
        return '\n'.join([border_row] + [''.join(row) for row in board] + [border_row])

    def is_game_over(self):
        # Game over if any cactus reaches the Dinosaur
        return any(pos == self.dino_position[1] for pos in self.cacti_positions)


class DinoGameView(View):
    def __init__(self, game):
        super().__init__()
        self.game = game

    @button(label="Jump", style=ButtonStyle.green, custom_id="jump")
    async def jump(self, button_signature, interaction):
        # Jump logic
        self.game.jump()
        # Update the message directly using the interaction
        await interaction.response.edit_message(content=self.game.get_state()["board"], view=self)

    async def update_board(self, channel, message_id):
        # Fetch the message using its ID
        try:
            message = await channel.fetch_message(message_id)
        except Exception as e:
            print(f"Failed to fetch message: {e}")
            return

        # Update the message
        game_state = self.game.get_state()
        if not game_state["game_over"]:
            await message.edit(content=game_state["board"], view=self)
        else:
            await message.edit(content="Game Over!", view=None)


class Cog(commands.Cog, name="DinoGame"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="dino", description="Play the Dino game")
    async def start_dino_game(self, ctx):
        frame_rate = 1
        game = DinoGame(frame_rate)
        view = DinoGameView(game)

        try:
            # Attempt to send the initial game message
            message = await ctx.send(game.get_state()["board"], view=view)
            if message:
                message_id = message.id  # Store the message ID
            else:
                print("Failed to send initial game message. Message object is None.")
                return
        except Exception as e:
            print(f"Failed to send initial game message: {e}")
            return

        # Continue with the game loop
        while not game.get_state()["game_over"]:
            await asyncio.sleep(frame_rate)
            game.update()
            try:
                await view.update_board(ctx.channel, message_id)
            except Exception as e:
                print(f"Error updating game: {e}")
                break




def setup(bot):
    bot.add_cog(Cog(bot))
