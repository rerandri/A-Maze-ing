import os
import random

from mazegen import MazeGenerator


class AsciiRenderer:
    WALL = {
        (False, False, False, False): ' ',
        (True,  False, False, False): '╹',
        (False, True,  False, False): '╻',
        (False, False, True,  False): '╺',
        (False, False, False, True): '╸',
        (True,  True,  False, False): '┃',
        (False, False, True,  True): '━',
        (True,  False, True,  False): '┗',
        (True,  False, False, True): '┛',
        (False, True,  True,  False): '┏',
        (False, True,  False, True): '┓',
        (True,  True,  True,  False): '┣',
        (True,  True,  False, True): '┫',
        (False, True,  True,  True): '┳',
        (True,  False, True,  True): '┻',
        (True,  True,  True,  True): '╋',
    }

    def __init__(self, maze: MazeGenerator) -> None:
        self.maze = maze

    def hex_to_walls(self, cell: int) -> tuple[bool, bool, bool, bool]:
        n = bool(cell & 0b0001)
        s = bool(cell & 0b0100)
        e = bool(cell & 0b0010)
        w = bool(cell & 0b1000)
        return (n, s, e, w)

    def display(self) -> None:
        height = self.maze.height
        width = self.maze.width
        inner = width * 2 - 1

        print('┏' + '━' * inner + '┓')

        for row_idx in range(height):
            out = ['┃']
            for col_idx in range(width):
                cell = self.maze.grid[row_idx][col_idx]
                n = bool(cell & 0b0001)
                s = bool(cell & 0b0100)
                e = bool(cell & 0b0010)
                w = bool(cell & 0b1000)
                e_orig = e

                if row_idx == 0:
                    n = False
                if row_idx == height - 1:
                    s = False
                if col_idx == 0:
                    w = False
                if col_idx == width - 1:
                    e = False

                out.append(self.WALL[(n, s, e, w)])
                if col_idx < width - 1:
                    out.append('━' if e_orig else ' ')
            out.append('┃')
            print(''.join(out))

        print('┗' + '━' * inner + '┛')


    def run_iterative(self) -> None:
        while True:
            print("\n\033[1m=== A-Maze-ing ===\033[0m")
            print("[1]. Re-generate a new maze")
            print("[2]. Display maze")
            print("[3]. Quit")
            try:
                print("\033[1;05mMaze>> \033[0m", end="", flush=True)
                answer = input().strip()
            except (KeyboardInterrupt, EOFError):
                print("\nOperation cancelled.\n")
                break
            if answer == "1":
                os.system('clear')
                self.maze.seed = random.randint(0, 2**32)
                self.maze._generated = False
                self.maze.generate()
                self.display()
            elif answer == "2":
                os.system('clear')
                self.display()
            elif answer == "3" or answer.lower() in ("quit", "exit"):
                print(" ... Exiting Terminal Interface ...\n")
                break
            else:
                print("\033[1;31mInvalid choice.\033[0m\n")


def help() -> None:
    print("\033[1m=== HELP PANNEL ===\033[0m")
    print("--- Interface")