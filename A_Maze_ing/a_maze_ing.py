import sys

from display import AsciiRenderer
from mazegen import MazeGenerator, parse_config, read_config_file


def main(argv: list[str] | None = None) -> None:
    """Generate a maze from a configuration file."""
    args = sys.argv if argv is None else argv
    if len(args) != 2:
        print("Usage: python a_maze_ing.py <config_file>", file=sys.stderr)
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
        )
        maze.generate()
        output_lines: list[str] = [
            *maze.to_hex_lines(),
            "",
            f"{maze.entry[0]},{maze.entry[1]}",
            f"{maze.exit[0]},{maze.exit[1]}",
            "".join(maze.get_solution()),
        ]
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(output_lines) + "\n")
            print(f"Maze generated and saved to '{output_file}'")
            renderer = AsciiRenderer(maze)
            renderer.run_iterative()
        except OSError as err:
            print(f"Error writing to file: {err}", file=sys.stderr)
            sys.exit(1)
    except FileNotFoundError:
        print(
            f"Error: Configuration file not found at '{config_file}'",
            file=sys.stderr,
        )
        sys.exit(1)
    except (ValueError, TypeError) as err:
        print(
            f"Error processing configuration or generating maze: {err}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
