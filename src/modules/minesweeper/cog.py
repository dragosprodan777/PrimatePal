from disnake.ext import commands
from disnake.ui import View, Button
from disnake import ButtonStyle
import disnake
import random
# Workaround with loading message


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
    def __init__(self, game=None, difficulty=None):  # Add difficulty parameter
        super().__init__()
        self.game = game
        self.difficulty = difficulty  # Store it

        if game is None:
            self.add_item(Button(style=ButtonStyle.green, label="Easy", custom_id="easy"))
            self.add_item(Button(style=ButtonStyle.blurple, label="Medium", custom_id="medium"))
            self.add_item(Button(style=ButtonStyle.red, label="Hard", custom_id="hard"))
        else:
            for x in range(game.rows):
                for y in range(game.cols):
                    self.add_item(Button(style=ButtonStyle.secondary, label="⬜", custom_id=f"cell_{x}_{y}"))

    async def start_game(self, interaction, mines):
        rows = cols = 5
        difficulty_level = interaction.data["custom_id"]

        game = MinesweeperGame(rows, cols, mines)
        new_view = MinesweeperView(game, difficulty_level)  # Pass the difficulty here

        difficulty_info = f"Difficulty: {difficulty_level.capitalize()} - Number of mines: {mines}."
        await interaction.response.edit_message(content=difficulty_info, view=new_view)


    async def interaction_check(self, interaction: disnake.Interaction):
        custom_id = interaction.data["custom_id"]

        if custom_id in ["easy", "medium", "hard"]:
            bombs = self.difficulty_to_mines(custom_id)
            await self.start_game(interaction, bombs)
            return False

        if "cell_" in custom_id:
            x, y = map(int, custom_id.split("_")[1:3])  # Extract the x and y coordinates from the custom_id
            revealed_cells = self.game.reveal(x, y)
            self.update_board_view()  # Update the buttons
            await self.render_board(interaction, revealed_cells)
            return False

        return True

    def update_board_view(self):
        for x in range(self.game.rows):
            for y in range(self.game.cols):
                if self.game.revealed[x][y]:
                    if self.game.board[x][y] == 'X':
                        self.children[x * self.game.cols + y].label = '💥'
                        self.children[x * self.game.cols + y].style = ButtonStyle.danger
                    elif self.game.board[x][y] == 0:
                        self.children[x * self.game.cols + y].label = '⬛'
                        self.children[x * self.game.cols + y].style = ButtonStyle.secondary
                    else:
                        self.children[x * self.game.cols + y].label = str(self.game.board[x][y])
                        self.children[x * self.game.cols + y].style = ButtonStyle.primary
                else:
                    self.children[x * self.game.cols + y].label = '⬜'
                    self.children[x * self.game.cols + y].style = ButtonStyle.secondary

    async def render_board(self, interaction, revealed_cells):
        content = f"Difficulty: {self.difficulty.capitalize()}" \
                  f" - Number of mines: {self.difficulty_to_mines(self.difficulty)}."

        if self.game.game_over:
            content = "💥 BOOM! Game Over!\n" + content

        await interaction.response.edit_message(content=content, view=self)

    def difficulty_to_mines(self, difficulty):
        # Mapping difficulty levels to the number of mines
        return {
            "easy": 3,
            "medium": 4,
            "hard": 5
        }[difficulty]


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
