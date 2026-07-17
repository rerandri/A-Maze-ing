import random
import shutil
import sys
import os
import time

from .color import Color
from mazegen import MazeGenerator
from solve import Solve_bfs


class AsciiRenderer:
    ANIM_DURATION: float = 1.5

    def __init__(self, maze: MazeGenerator) -> None:
        self.maze: MazeGenerator = maze
        self.delay: float = 0.03
        self.solve = Solve_bfs(maze)

        self._last_render_lines: int = 0
        self.count_invalid_inputs: int = 0
        self.show_path: bool = False
        self.animate_reveal: bool = True

        self.c: Color = Color()

        combinaison = self.c.get_comb()
        idx = random.randint(0, len(combinaison) - 1)
        self.wall = combinaison[idx][0] + "██" + self.c.end()
        self.way = combinaison[idx][1] + "██" + self.c.end()

        self.blocked: str = self.c.rgb(255, 100, 100) + "██" + self.c.end()
        self.path: str = self.c.rgb(0, 255, 0) + "██" + self.c.end()
        self.start: str = self.c.rgb(0, 0, 255) + "██" + self.c.end()
        self.end: str = self.c.rgb(255, 0, 0) + "██" + self.c.end()

    def _build_pixels(self) -> list[list[str]]:
        cols: int = self.maze.width * 2 + 1
        rows: int = self.maze.height * 2 + 1
        pixels: list[list[str]] = [
            [self.wall for _ in range(cols)] for _ in range(rows)
        ]

        for y in range(self.maze.height):
            for x in range(self.maze.width):

                if (x, y) in self.maze._blocked:
                    pixels[2 * y + 1][2 * x + 1] = self.blocked
                else:
                    pixels[2 * y + 1][2 * x + 1] = self.way

                if not self.maze.has_wall(x, y, MazeGenerator.NORTH):
                    pixels[2 * y][2 * x + 1] = self.way
                if not self.maze.has_wall(x, y, MazeGenerator.SOUTH):
                    pixels[2 * y + 2][2 * x + 1] = self.way
                if not self.maze.has_wall(x, y, MazeGenerator.EAST):
                    pixels[2 * y + 1][2 * x + 2] = self.way
                if not self.maze.has_wall(x, y, MazeGenerator.WEST):
                    pixels[2 * y + 1][2 * x] = self.way

        return pixels

    def _maze_fits(self) -> bool:
        term_cols, term_lines = shutil.get_terminal_size(fallback=(80, 24))
        needed_cols = (self.maze.width * 2 + 1) * 2
        needed_lines = self.maze.height * 2 + 1 + 2
        return term_cols >= needed_cols and term_lines >= needed_lines

    def _flush_render(self, pixels: list[list[str]]) -> None:
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
        thresholds = [(130, 64), (100, 32), (80, 16), (60, 8), (40, 4)]
        for limit, chunk in thresholds:
            if maze_width >= limit:
                return chunk
        return 1

    def _animate_reveal(self, pixels: list[list[str]]) -> None:
        total_rows = len(pixels)
        chunk = self._reveal_chunk_size(self.maze.width)
        steps = (total_rows + chunk - 1) // chunk
        step_delay = self.ANIM_DURATION / steps

        width = len(pixels[0])
        canvas = [
            [self.wall for _ in range(width)] for _ in range(total_rows)
        ]

        for i in range(0, total_rows, chunk):
            end = min(i + chunk, total_rows)
            for r in range(i, end):
                canvas[r] = pixels[r]
            self._flush_render(canvas)
            time.sleep(step_delay)

        self._flush_render(pixels)

    def display(
        self, show_path: bool = False, animate: bool | None = None
    ) -> None:
        self.show_path = show_path
        if animate is None:
            animate = self.animate_reveal

        if not self._maze_fits():
            needed_cols = (self.maze.width * 2 + 1) * 2
            needed_lines = self.maze.height * 2 + 1 + 2
            term_cols, term_lines = shutil.get_terminal_size(fallback=(80, 24))
            print(
                Color.error(
                    f"Terminal too small"
                    f" ({term_cols}x{term_lines}) to display"
                    f" maze (needs {needed_cols}x{needed_lines})."
                    "Resize and try again."
                ),
                flush=True,
            )
            return

        entry_x, entry_y = self.maze.entry
        exit_x, exit_y = self.maze.exit
        pixels: list[list[str]] = self._build_pixels()
        pixels[2 * entry_y + 1][2 * entry_x + 1] = self.start
        pixels[2 * exit_y + 1][2 * exit_x + 1] = self.end

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
                pixels[2 * curr_y][2 * curr_x + 1] = self.path
                curr_y -= 1
            elif move == "S":
                pixels[2 * curr_y + 2][2 * curr_x + 1] = self.path
                curr_y += 1
            elif move == "E":
                pixels[2 * curr_y + 1][2 * curr_x + 2] = self.path
                curr_x += 1
            elif move == "W":
                pixels[2 * curr_y + 1][2 * curr_x] = self.path
                curr_x -= 1
            pixels[2 * curr_y + 1][2 * curr_x + 1] = self.path
            self._flush_render(pixels)
            time.sleep(self.delay)

        pixels[2 * exit_y + 1][2 * exit_x + 1] = self.end
        self._flush_render(pixels)

    def _menu_prompt(self) -> str | None:
        """Return user input, or None on interrupt."""
        path_on = '[ON]' if self.show_path else '[OFF]'
        anim_on = '[ON]' if self.animate_reveal else '[OFF]'
        print("\n\033[1m=== A-Maze-ing ===\033[0m")
        print(
            f" [1].Re-generate maze\n"
            f" [2].Display maze\n"
            f" [3].Show path: {path_on}\n"
            f" [4].Reveal animation: {anim_on}\n"
            f" [5].Rotate maze colors\n"
            f" [6].Cycle '42' pattern colors")
        print(" [7].Quit")

        print(self.c.info("\nType /help for more commands."))
        try:
            print("\033[1mMaze>> \033[0m", end="", flush=True)
            return input().strip(' ')
        except (KeyboardInterrupt, EOFError):
            print(Color.info("\nOperation cancelled.\n"))
            return None

    def _handle_regenerate(self) -> None:
        os.system('clear')
        self.maze.seed = random.randint(0, 2**32)
        self.maze._generated = False
        self.maze.generate()
        self.display(show_path=self.show_path)

    def _handle_display(self) -> None:
        os.system('clear')
        self.display(show_path=self.show_path)
        self.header()

    def _handle_toggle_path(self) -> None:
        os.system('clear')
        self.show_path = not self.show_path
        self.display(show_path=self.show_path, animate=False)
        self.header()

    def _handle_toggle_animation(self) -> None:
        os.system('clear')
        self.animate_reveal = not self.animate_reveal
        state = 'enabled' if self.animate_reveal else 'disabled'
        print(f"Reveal animation {state}.\n")

    def _handle_rotate_colors(self) -> None:
        os.system('clear')
        combinaison = self.c.get_comb()
        idx = random.randint(0, len(combinaison) - 1)
        self.show_path = False
        self.wall = combinaison[idx][0] + "██" + self.c.end()
        self.way = combinaison[idx][1] + "██" + self.c.end()
        self.display(show_path=self.show_path, animate=False)

    def _handle_cycle_blocked(self) -> None:
        os.system('clear')
        combinaison = self.c.get_comb()
        idx = random.randint(0, len(combinaison) - 1)
        self.show_path = False
        self.blocked = combinaison[idx][0] + "██" + self.c.end()
        self.display(show_path=self.show_path, animate=False)

    def _handle_delay(self, value: str) -> None:
        print(Color.info(
            f"Setting animation delay... {value}"
        ))
        try:
            tmp_delay = float(value)
            if tmp_delay < 0.0:
                raise ValueError("Delay cannot be negative.")
            self.delay = tmp_delay
            if self.delay > 0.1:
                print(Color.warning(
                    f"Delay {self.delay}s is quite long. Consider using a "
                    f"smaller value for a better experience."
                ))
            print(Color.success(
                f"Animation delay set to {self.delay}s.\n"
            ))
        except ValueError:
            print(Color.error("Invalid delay value. Enter a valid number.\n"))

    def _handle_clear(self) -> None:
        os.system('clear')

    def _handle_help(self) -> None:
        os.system('clear')
        show_help()

    def _handle_info(self) -> None:
        os.system('clear')
        temp_delay = self.delay
        if self.show_path:
            self.delay = 0.0
        self.display(show_path=self.show_path, animate=False)
        self.delay = temp_delay
        self.header()

    def _handle_quit(self) -> bool:
        print(Color.info(" ... Exiting Terminal Interface ...\n"))
        return True

    def _handle_set_colors(self) -> None:
        os.system('clear')
        print(Color.info("Setting custom colors for maze elements."))
        try:
            print(f"{'Enter RGB format (e.g: 255, 0, 0)':>50}\n")
            wall_color = input("Enter wall color (RGB format): ")
            self.wall = (
                self.c.rgb(*map(int, wall_color.split(',')))
                + "██" + self.c.end()
            )
            print(Color.success(
                f"Wall color set successfully -- {self.wall}.\n"
            ))
            blocked_color = input("Enter '42' pattern color (RGB): ")
            self.blocked = (
                self.c.rgb(*map(int, blocked_color.split(',')))
                + "██" + self.c.end()
            )
            print(Color.success(
                f"Blocked color set successfully -- {self.blocked}.\n"
            ))
        except Exception as e:
            print(Color.error(
                f"Could not set custom colors: {e}\n"
            ))

    def _handle_invalid(self) -> None:
        if self.count_invalid_inputs >= 4:
            os.system('clear')
            self.count_invalid_inputs = 0
        self.count_invalid_inputs += 1
        print(Color.error("Invalid choice.\n"))

    def run_iterative(self) -> None:
        self.wall = self.c.random_color() + "██" + self.c.end()
        self.blocked = self.c.random_color() + "██" + self.c.end()

        while True:
            answer = self._menu_prompt()
            if answer is None:
                break
            if answer == "1":
                self._handle_regenerate()
            elif answer == "2":
                self._handle_display()
            elif answer == "3":
                self._handle_toggle_path()
            elif answer == "4":
                self._handle_toggle_animation()
            elif answer == "5":
                self._handle_rotate_colors()
            elif answer == "6":
                self._handle_cycle_blocked()
            elif answer.startswith("/delay ") or answer.startswith("/d "):
                delay_val = (
                    answer.removeprefix("/delay ")
                    .removeprefix("/d ").strip()
                )
                self._handle_delay(delay_val)
            elif answer in ("/clear", "/c"):
                self._handle_clear()
            elif answer in ("/help", "/h"):
                self._handle_help()
            elif answer in ("/info", "/i"):
                self._handle_info()
            elif answer in ("7", "quit", "exit"):
                if self._handle_quit():
                    break
            elif answer in ("/setcolors", "/sc"):
                self._handle_set_colors()
            else:
                self._handle_invalid()

    def header(self) -> None:
        enter = self.start
        exit = self.end
        path = self.path
        print(
            "\033[1mInfo for maze:\033[0m\n"
            f"Entry : {enter} | Exit : {exit} | Path : {path}"
            f" | wall : {self.wall} | '42' pattern : {self.blocked}\n\n"
            f"Size : {self.maze.width} x {self.maze.height}\n"

            f"Animation delay : {self.delay}s"
            f"\nReveal animation :"
            f" {'ON' if self.animate_reveal else 'OFF'}\n"
            f"Show path : {'ON' if self.show_path else 'OFF'}\n"
        )


def show_help() -> None:
    os.system('clear')
    print(
        "\033[1m=== A-Maze-ing Help ===\033[0m\n"
        "This program generates and displays mazes"
        " in the terminal.\n\n"
        "\033[1m**  Menu Options:\033[0m\n"
        f"1. {'Re-generate a new maze':<35}"
        " : Creates a new maze with a random seed.\n"
        f"2. {'Display maze':<35}"
        " : Shows the current maze in the terminal.\n"
        f"3. {'Show/Hide path':<35}"
        " : Toggles the solution path display.\n"
        f"4. {'Toggle reveal animation':<35}"
        " : Enables or disables animation.\n"
        f"5. {'Rotate maze colors':<35}"
        " : Changes the wall color scheme.\n"
        f"6. {'Cycle 42 pattern':<35}"
        " : Changes blocked cell colors.\n"
        f"7. {'Quit':<35} : Exits the program.\n\n"
        "\033[1mAdditional Commands:\033[0m\n"
        f"8. {'/clear or /c':<30} : Clears the screen.\n"
        f"9. {'/help or /h':<30} : Shows this help.\n"
        f"10. {'/delay <s> or /d <s>':<30}"
        " : Sets animation speed.\n"
        f"11. {'/info or /i':<30}"
        " : Shows maze info.\n\n"
        f"12. {'/setcolors or /sc':<30}"
        " : Sets custom colors.\n"
    )
