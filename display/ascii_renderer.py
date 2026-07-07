import random
import shutil
import sys
import os
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

    ANIM_DURATION: float = 1.5

    def __init__(self, maze: MazeGenerator) -> None:
        """Initialize the renderer with a generated maze instance.
        Args:
            maze: A fully generated MazeGenerator instance.
        """
        self.maze: MazeGenerator = maze
        self.delay: float = 0.03
        self._clamp_maze_to_terminal()
        self.solve = Solve_bfs(maze)
        self._color_index: int = 0
        self._blocked42_index: int = 0
        self.show_path: bool = False
        self.animate_reveal: bool = True
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

    @staticmethod
    def _reveal_chunk_size(maze_width: int) -> int:
        """Adaptive chunk size: wider mazes reveal more rows per frame."""
        thresholds = [(130, 64), (100, 32), (80, 16), (60, 8), (40, 4)]
        for limit, chunk in thresholds:
            if maze_width >= limit:
                return chunk
        return 1

    def _animate_reveal(self, pixels: list[list[str]]) -> None:
        """Animate the maze appearing row by row.

        Groups pixel rows into chunks for performance — wider mazes
        reveal more rows per frame so the total frame count stays
        roughly constant.
        """
        total_rows = len(pixels)
        chunk = self._reveal_chunk_size(self.maze.width)
        steps = (total_rows + chunk - 1) // chunk
        step_delay = self.ANIM_DURATION / steps

        canvas = [
            [self.EMPTY for _ in range(len(pixels[0]))] for _ in range(total_rows)
        ]

        for i in range(0, total_rows, chunk):
            end = min(i + chunk, total_rows)
            for r in range(i, end):
                canvas[r] = pixels[r]
            self._flush_render(canvas)
            time.sleep(step_delay)

        self._flush_render(pixels)

    def display(self, show_path: bool = False, animate: bool | None = None) -> None:
        """Display the maze and optionally animate the solution path.

        If the terminal is too small, prints an error in red and returns.
        When show_path is True, animates the shortest path from entry to exit
        using green cells with a small delay between steps.

        Args:
            show_path: Whether to animate the solution path.
            animate: Whether to animate the maze reveal. Defaults to
                     self.animate_reveal if not set.
        """
        self.show_path = show_path
        if animate is None:
            animate = self.animate_reveal

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

        if animate:
            self._animate_reveal(pixels)
        else:
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
        while True:
            print("\033[1m=== A-Maze-ing ===\033[0m")
            print("[1]. Re-generate a new maze")
            print("[2]. Display maze")
            print(f"[3]. {'Hide' if self.show_path else 'Show'} path from entry to exit")
            print(f"[4]. Toggle reveal animation {'[ON]' if self.animate_reveal else '[OFF]'}")
            print("[5]. Rotate maze colors")
            print("[6]. Cycle '42' pattern colors")
            print("[7]. Quit")
            print("\033[33mType /help for more commands.\033[0m")
            try:
                print("\033[05mMaze>> \033[0m", end="", flush=True)
                answer: str = input().strip(' ')
            except (KeyboardInterrupt, EOFError):
                print("\nOperation cancelled.\n")
                break
            if answer == "1":
                self._clamp_maze_to_terminal()
                self.maze.seed = random.randint(0, 2**32)
                self.maze._generated = False
                self.maze.generate()
                self.display(show_path=self.show_path)
            elif answer == "2":
                self.display(show_path=self.show_path)
            elif answer == "3":
                self.show_path = not self.show_path
                self.display(show_path=self.show_path, animate=False)
            elif answer == "4":
                self.animate_reveal = not self.animate_reveal
                print(
                    f"Reveal animation {'enabled' if self.animate_reveal else 'disabled'}.\n"
                )
            elif answer == "5":
                self._color_index = (self._color_index + 1) % len(
                    self.WALL_OPTIONS
                )
                self.EMPTY = self.WALL_OPTIONS[self._color_index]
                self.display(show_path=self.show_path, animate=False)
            elif answer == "6":
                self._blocked42_index = (
                    self._blocked42_index + 1
                ) % len(self.BLOCKED42_OPTIONS)

                self.BLOCKED = self.BLOCKED42_OPTIONS[self._blocked42_index]
                self.display(show_path=self.show_path, animate=False)
            elif answer.startswith("/delay ") or answer.startswith("/d "):
                answer = answer.removeprefix("/delay ").removeprefix("/d ").strip()
                print(f"Setting animation delay... {answer}")
                try:
                    tmp_delay = float(answer)
                    if tmp_delay < 0.0:
                        raise ValueError("Delay cannot be negative.")
                    elif tmp_delay > 0.1:
                        raise ValueError(
                            "Warning: Delay is quite long. Consider using a smaller "
                            "value for better experience."
                        )
                    else:
                        self.delay = tmp_delay
                        print(f"Animation delay set to {self.delay} seconds.\n")
                except (ValueError, IndexError):
                    print("Invalid delay value. Please enter a valid number.\n")
            elif answer == "/clear".strip() or answer == "/c".strip():
                os.system('clear')
            elif answer == "/help".strip() or answer == "/h".strip():
                os.system('clear')
                help()
            elif answer == "/info".strip() or answer == "/i".strip():
                os.system('clear')
                self.display(show_path=self.show_path, animate=False)
                self.header()
            elif answer == "7" or answer.lower() == "quit" or answer.lower() == "exit":
                print("Bye!")
                break
            else:
                print("Invalid choice.\n")

    def header(self):
        enter = self.START
        exit = self.END
        path = self.PATH
        print(
            "Info for maze:\n"
            f"  Maze dimensions : {self.maze.width} x {self.maze.height:<10}\n"
            f"  Enter           : {enter:<15}\n"
            f"  Exit            : {exit:<15}\n"
            f"  Path            : {path:<15}\n"
            f"  animation reveal: {'ON' if self.animate_reveal else 'OFF':<15}\n"
            f"  Animation delay : {self.delay:<15}\n")


def help() -> None:
    os.system('clear')
    """Print usage instructions for the ascii renderer."""
    print(
        "\033[1m=== A-Maze-ing Help ===\033[0m\n"
        "This program generates and displays mazes in the terminal.\n\n"
        "\033[1m**  Menu Options:\033[0m\n"
        f"1. {'Re-generate a new maze':<35} : Creates a new maze with a random seed.\n"
        f"2. {'Display maze':<35} : Shows the current maze in the terminal.\n"
        f"3. {'Show/Hide path from entry to exit':<35} : Toggles the display of the solution path.\n"
        f"4. {'Toggle reveal animation':<35} : Enables or disables the animation when revealing the maze.\n"
        f"5. {'Rotate maze colors':<35} : Changes the color scheme of the maze walls.\n"
        f"6. {'Cycle 42 pattern colors':<35} : Changes the color scheme of blocked cells.\n"
        f"7. {'Quit':<35} : Exits the program.\n\n"
        "\033[1m**  Additional Commands:\033[0m\n"
        f"8. {'/clear or /c':<35} : Clears the terminal screen.\n"
        f"9. {'/help or /h':<35} : Displays this help message.\n"
        f"10. {'/delay <seconds> or /d <seconds>':<34} : Updates the animation speed.\n"
        f"11. {'/info or /i':<34} : Displays information about the maze, including entry, exit, and path symbols.\n\n"
    )