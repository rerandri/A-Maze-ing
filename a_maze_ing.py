import sys
import os
from display import AsciiRenderer
from display.color import Color
from mazegen import MazeGenerator
from parser import read_config_file, parse_config
from solve import Solve_bfs


def main(argv: list[str] | None = None) -> None:
    os.system('clear')
    """Generate a maze from a configuration file."""
    args = sys.argv if argv is None else argv
    if len(args) != 2:
        print(
            Color.info("Usage: python a_maze_ing.py <config_file>"),
            file=sys.stderr,
        )
        sys.exit(1)

    config_file = args[1]
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            raw = read_config_file(f)
        raw_config = parse_config(raw)
        output_file = raw_config["OUTPUT_FILE"]
        maze = MazeGenerator(
            width=raw_config["WIDTH"],
            height=raw_config["HEIGHT"],
            entry=raw_config["ENTRY"],
            exit=raw_config["EXIT"],
            seed=raw_config["SEED"],
            perfect=raw_config["PERFECT"],
        )
        maze.generate()
        solve = Solve_bfs(maze)
        output_lines: list[str] = [
            *maze.to_hex_lines(),
            "",
            f"{maze.entry[0]},{maze.entry[1]}",
            f"{maze.exit[0]},{maze.exit[1]}",
            "".join(solve.get_solution()),
        ]
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(output_lines) + "\n")
            print(Color.info(
                f"Generating maze with dimensions"
                f" {maze.width}x{maze.height} ..."
            ))
            print(Color.success(
                f"Maze generated and saved to '{output_file}'"
            ))
            renderer = AsciiRenderer(maze)
            try:
                renderer.run_iterative()
            except (KeyboardInterrupt, EOFError):
                print(Color.warning("\nOperation cancelled on Renderer.\n"))
        except OSError as err:
            print(
                Color.error(
                    f"Could not write to output file"
                    f" '{output_file}': {err}"
                ),
                file=sys.stderr,
            )
            sys.exit(1)
    except FileNotFoundError:
        print(
            Color.error(f"Configuration file not found at '{config_file}'"),
            file=sys.stderr,
        )
        sys.exit(1)
    except (ValueError, TypeError) as err:
        print(
            Color.error(f"Invalid configuration: {err}"),
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
