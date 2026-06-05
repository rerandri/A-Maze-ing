import random
import time

from mazegen import MazeGenerator

class Color:
    RESET = "\033[0m"
    BG_WHITE = "\033[107m"
    BG_BLACK = "\033[100m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_BLUE = "\033[44m"
    BG_CYAN = "\033[46m"
    BG_PURPLE = "\033[45m"


class AsciiRenderer:
    """Render a maze using terminal-friendly characters."""
    C = Color()
    BLOCK_CHAR: str = "  " + C.RESET
    WALL_OPTIONS = [
        C.BG_WHITE + BLOCK_CHAR,
        C.BG_CYAN + BLOCK_CHAR,
        C.BG_PURPLE + BLOCK_CHAR,
    ]

    EMPTY: str = WALL_OPTIONS[0]
    BACKGROUND: str = C.BG_BLACK + BLOCK_CHAR
    BLOCKED: str = C.BG_PURPLE + BLOCK_CHAR
    PATH: str = C.BG_GREEN + BLOCK_CHAR
    START: str = C.BG_BLUE + BLOCK_CHAR
    END: str = C.BG_RED + BLOCK_CHAR

    def __init__(self, maze: MazeGenerator) -> None:
        """Initialize the renderer with a generated maze instance."""
        self.maze: MazeGenerator = maze
        self._color_index: int = 0
        self.show_path: bool = False

    def _build_pixels(self) -> list[list[str]]:
        """Build a 2D character matrix representing the maze."""
        cols: int = self.maze.width * 2 + 1
        rows: int = self.maze.height * 2 + 1
        pixels: list[list[str]] = [
            [self.EMPTY for _ in range(cols)] for _ in range(rows)
        ]

        for y in range(self.maze.height):
            for x in range(self.maze.width):

                if (x, y) in self.maze._blocked:
                    pixels[2 * y + 1][2 * x + 1] = self.BLOCKED
                else:
                    pixels[2 * y + 1][2 * x + 1] = self.BACKGROUND

                if not self.maze.has_wall(x, y, MazeGenerator.NORTH):
                    pixels[2 * y][2 * x + 1] = self.BACKGROUND
                if not self.maze.has_wall(x, y, MazeGenerator.SOUTH):
                    pixels[2 * y + 2][2 * x + 1] = self.BACKGROUND
                if not self.maze.has_wall(x, y, MazeGenerator.EAST):
                    pixels[2 * y + 1][2 * x + 2] = self.BACKGROUND
                if not self.maze.has_wall(x, y, MazeGenerator.WEST):
                    pixels[2 * y + 1][2 * x] = self.BACKGROUND

        return pixels

    def render(self) -> str:
        """Return the maze rendering as a single string."""
        pixels: list[list[str]] = self._build_pixels()
        rendered: str = "\n".join("".join(row) for row in pixels)
        return rendered

    def display(self, show_path: bool = False) -> None:
        """Display the maze and optionally animate the solution path."""
        self.show_path = show_path
        entry_x, entry_y = self.maze.entry
        exit_x, exit_y = self.maze.exit
        pixels: list[list[str]] = self._build_pixels()
        pixels[2 * entry_y + 1][2 * entry_x + 1] = self.START
        pixels[2 * exit_y + 1][2 * exit_x + 1] = self.END

        def _refresh() -> None:
            print("\033[H", end="", flush=True)
            print("\n".join("".join(row) for row in pixels), flush=True)
            time.sleep(0.02)

        print("\033[2J\033[H", end="", flush=True)
        print("\n".join("".join(row) for row in pixels), flush=True)

        if not show_path:
            return

        curr_x, curr_y = self.maze.entry
        for move in self.maze.get_solution():
            if move == "N":
                pixels[2 * curr_y][2 * curr_x + 1] = self.PATH
                curr_y -= 1
            elif move == "S":
                pixels[2 * curr_y + 2][2 * curr_x + 1] = self.PATH
                curr_y += 1
            elif move == "E":
                pixels[2 * curr_y + 1][2 * curr_x + 2] = self.PATH
                curr_x += 1
            elif move == "W":
                pixels[2 * curr_y + 1][2 * curr_x] = self.PATH
                curr_x -= 1
            pixels[2 * curr_y + 1][2 * curr_x + 1] = self.PATH
            _refresh()

        pixels[2 * exit_y + 1][2 * exit_x + 1] = self.END
        _refresh()

    def run_iterative(self) -> None:
        """Run the interactive terminal menu for maze actions."""
        print("=== A-Maze-ing ===")
        while True:
            print("1. Re-generate a new maze")
            print("2. Show/Hide path from entry to exit")
            print("3. Rotate maze colors")
            print("4. Quit\nChoice? (1-4): ", end="", flush=True)
            try:
                answer: str = input()
            except (KeyboardInterrupt, EOFError):
                print("\nOperation cancelled.")
                break
            if answer == "1":
                self.maze.seed = random.randint(0, 2**32)
                self.maze.entry = (
                    random.randint(0, self.maze.width - 1),
                    random.randint(0, self.maze.height - 1),
                )
                self.maze.exit = (
                    random.randint(0, self.maze.width - 1),
                    random.randint(0, self.maze.height - 1),
                )
                self.maze._generated = False
                self.maze.generate()
                self.display(show_path=self.show_path)
            elif answer == "2":
                self.show_path = not self.show_path
                self.display(show_path=self.show_path)
            elif answer == "3":
                self._color_index = (self._color_index + 1) % len(
                    self.WALL_OPTIONS
                )
                self.EMPTY = self.WALL_OPTIONS[self._color_index]
                self.display(show_path=self.show_path)
            elif answer == "4":
                print("Bye!")
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 4.")
