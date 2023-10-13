from disnake.ext import commands
from disnake.ui import View, button
from disnake import ButtonStyle
import random


class MinesweeperGame:
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.board = self.generate_board(rows, cols, mines)
        self.revealed = [[False for _ in range(cols)] for _ in range(rows)]
        self.game_over = False

    def generate_board(self, rows, cols, mines):
        board = [[0 for _ in range(cols)] for _ in range(rows)]

        mine_positions = random.sample([(r, c) for r in range(rows) for c in range(cols)], mines)

        for (x, y) in mine_positions:
            board[x][y] = 'X'
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < rows and 0 <= ny < cols and board[nx][ny] != 'X':
                        board[nx][ny] += 1

        return board

    def reveal(self, x, y):
        if self.revealed[x][y] or self.game_over:
            return []

        self.revealed[x][y] = True
        if self.board[x][y] == 'X':
            self.game_over = True
            return [(x, y, 'X')]

        revealed_cells = [(x, y, self.board[x][y])]
        if self.board[x][y] == 0:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.rows and 0 <= ny < self.cols and not self.revealed[nx][ny]:
                        revealed_cells.extend(self.reveal(nx, ny))

        return revealed_cells


class MinesweeperView(View):
    def __init__(self, game):
        super().__init__()
        self.game = game

    @button(label="Easy", style=ButtonStyle.green, custom_id="easy")
    async def on_easy_click(self, button_signature, interaction):
        await self.start_game(interaction, 5, 5)
        _ = button_signature

    @button(label="Medium", style=ButtonStyle.blurple, custom_id="medium")
    async def on_medium_click(self, button_signature, interaction):
        await self.start_game(interaction, 7, 7)
        _ = button_signature

    @button(label="Hard", style=ButtonStyle.red, custom_id="hard")
    async def on_hard_click(self, button_signature, interaction):
        await self.start_game(interaction, 9, 9)
        _ = button_signature

    async def start_game(self, interaction, rows, cols):
        game = MinesweeperGame(rows, cols, int(rows*cols*0.15)) # 15% of the board are mines
        self.game = game

        message = "Minesweeper game started!\n\n"
        for i in range(rows):
            for j in range(cols):
                message += ":white_large_square:" # Placeholder for unrevealed cells
            message += "\n"
        await interaction.response.edit_message(content=message, view=None)


class Cog(commands.Cog, name="Minesweeper"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="minesweeper",
        description="Play Minesweeper"
    )
    async def play_minesweeper(self, ctx):
        print(f"Received 'minesweeper' command from {ctx.author.name}")
        view = MinesweeperView(None)
        await ctx.send("Choose a difficulty level:", view=view)


def setup(bot):
    bot.add_cog(Cog(bot))
