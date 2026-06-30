import random
import shutil
import sys
import time

from mazegen import MazeGenerator
from solve import Solve_bfs


class AsciiRenderer:
    """Render a maze using terminal-friendly characters."""

    BLOCK_CHAR: str = "➖"
    BLOCK_WALL: str = "🟥"
    WALL_OPTIONS = [
        "🟩",
        "🟦",
        "🟨",
        "🟧"
    ]

    BLOCKED42_OPTIONS = [
        "⬜",
        "⬛",
        "🟪",
        "🟫",
    ]

    EMPTY: str = WALL_OPTIONS[0]
    BACKGROUND: str = BLOCK_CHAR
    BLOCKED: str = BLOCKED42_OPTIONS[0]
    PATH: str = "🛜 "
    START: str = "👽"
    END: str = "🛸"

    def __init__(self, maze: MazeGenerator) -> None:
        """Initialize the renderer with a generated maze instance.
        Args:
            maze: A fully generated MazeGenerator instance.
        """
        self.maze: MazeGenerator = maze
        self.delay: float = 0.0
        self._clamp_maze_to_terminal()
        self.solve = Solve_bfs(maze)
        self._color_index: int = 0
        self._blocked42_index: int = 0
        self.show_path: bool = False
        self._last_render_lines: int = 0
        self.EMPTY: str = self.WALL_OPTIONS[0]
        self.BACKGROUND: str = self.BLOCK_CHAR
        self.BLOCKED: str = self.BLOCKED42_OPTIONS[0]
        self.PATH: str = self.PATH
        self.START: str = self.START
        self.END: str = self.END

    def _build_pixels(self) -> list[list[str]]:
        """Build a 2D character matrix representing the maze.

        Returns:
            A 2D list where each inner list is a row of ANSI-colored strings.
            Dimensions are (height*2+1) x (width*2+1).
        """
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

    def _maze_fits(self) -> bool:
        """Check whether the maze fits in the current terminal window."""
        term_cols, term_lines = shutil.get_terminal_size(fallback=(80, 24))
        needed_cols = (self.maze.width * 2 + 1) * 2
        needed_lines = self.maze.height * 2 + 1 + 2
        return term_cols >= needed_cols and term_lines >= needed_lines

    def _clamp_maze_to_terminal(self) -> None:
        """Shrink maze dimensions so it fits in the current terminal.

        The maze is resized just enough to satisfy ``_maze_fits()``.
        If the maze was already generated, it is regenerated with the
        same seed after resizing.
        """
        term_cols, term_lines = shutil.get_terminal_size(
            fallback=(80, 24)
        )
        max_width: int = max(1, (term_cols - 2) // 4)
        max_height: int = max(1, (term_lines - 3) // 2)

        old_w, old_h = self.maze.width, self.maze.height
        self.maze.width = min(self.maze.width, max_width)
        self.maze.height = min(self.maze.height, max_height)

        if (self.maze.width, self.maze.height) == (old_w, old_h):
            return

        self.maze.entry = (
            min(self.maze.entry[0], self.maze.width - 1),
            min(self.maze.entry[1], self.maze.height - 1),
        )
        self.maze.exit = (
            min(self.maze.exit[0], self.maze.width - 1),
            min(self.maze.exit[1], self.maze.height - 1),
        )

        if self.maze._generated:
            self.maze._generated = False
            self.maze._blocked.clear()
            self.maze.generate()

    def _flush_render(self, pixels: list[list[str]]) -> None:
        """Write the full pixel grid to stdout in a single atomic write.

        Moves the cursor up by exactly the number of lines written last time,
        clears from there to end-of-screen, then writes the new frame.
        This avoids the duplicate-lines artifact caused by \033[H (absolute
        repositioning) when the terminal is small or the user has scrolled.
        """
        output = "\n".join("".join(row) for row in pixels)
        if self._last_render_lines > 0:
            preamble = f"\033[{self._last_render_lines}A\033[0J"
        else:
            preamble = ""
        sys.stdout.write(preamble + output + "\n")
        sys.stdout.flush()
        self._last_render_lines = len(pixels)

    def display(self, show_path: bool = False) -> None:
        """Display the maze and optionally animate the solution path.

        If the terminal is too small, prints an error in red and returns.
        When show_path is True, animates the shortest path from entry to exit
        using green cells with a small delay between steps.

        Args:
            show_path: Whether to animate the solution path.
            delay: The delay between steps in seconds.
        """
        self.show_path = show_path

        if not self._maze_fits():
            print(
                "\033[31mTerminal window too small to display the maze. "
                "Please resize and try again.\033[0m",
                flush=True,
            )
            return

        entry_x, entry_y = self.maze.entry
        exit_x, exit_y = self.maze.exit
        pixels: list[list[str]] = self._build_pixels()
        pixels[2 * entry_y + 1][2 * entry_x + 1] = self.START
        pixels[2 * exit_y + 1][2 * exit_x + 1] = self.END

        self._last_render_lines = 0
        self._flush_render(pixels)

        if not show_path:
            return

        curr_x, curr_y = self.maze.entry
        for move in self.solve.get_solution():
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
            self._flush_render(pixels)
            time.sleep(self.delay)

        pixels[2 * exit_y + 1][2 * exit_x + 1] = self.END
        self._flush_render(pixels)

    def run_iterative(self) -> None:
        """Run the interactive terminal menu for maze actions."""
        def header():
            enter = "👽"
            exit = "🛸"
            path = "🛜"
            print(
                "Info for maze:\n"
                f"  Enter           : {enter:<15}\n"
                f"  Exit            : {exit:<15}\n"
                f"  Path            : {path:<15}\n"    
                f"  Animation delay : {self.delay:<15}")
            print(
                "For delay, type 'delay=<seconds>' "
                "(e.g., delay=0.5) and press Enter.\n")
        header()
        while True:
            print("=== A-Maze-ing ===")
            print("[1]. Re-generate a new maze")
            print("[2]. Display maze")
            print("[3]. Show/Hide path from entry to exit")
            print("[4]. Rotate maze colors")
            print("[5]. Cycle '42' pattern colors")
            print("[6]. Quit\nChoice? : ", end="", flush=True)
            try:
                answer: str = input()
            except (KeyboardInterrupt, EOFError):
                print("\nOperation cancelled.\n")
                break
            if answer == "1":
                self._clamp_maze_to_terminal()
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
                self.display()
            elif answer == "3":
                self.show_path = not self.show_path
                self.display(show_path=self.show_path)
            elif answer == "4":
                self._color_index = (self._color_index + 1) % len(
                    self.WALL_OPTIONS
                )
                self.EMPTY = self.WALL_OPTIONS[self._color_index]
                self.display(show_path=self.show_path)
            elif answer == "5":
                self._blocked42_index = (
                    self._blocked42_index + 1
                ) % len(self.BLOCKED42_OPTIONS)

                self.BLOCKED = self.BLOCKED42_OPTIONS[self._blocked42_index]
                self.display(show_path=self.show_path)
            elif answer.startswith("delay="):
                try:
                    tmp_delay = float(answer.split("=")[1])
                    if tmp_delay < 0:
                        raise ValueError("Delay cannot be negative.")
                    elif tmp_delay > 1:
                        raise ValueError(
                            "Warning: Delay is quite long. Consider using a smaller "
                            "value for better experience."
                        )
                    else:
                        self.delay = tmp_delay
                        print(f"Animation delay set to {self.delay} seconds.\n")
                        header()
                except (ValueError, IndexError):
                    print("Invalid delay value. Please enter a valid number.\n")
            elif answer == "6":
                print("Bye!")
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 6.\n")
