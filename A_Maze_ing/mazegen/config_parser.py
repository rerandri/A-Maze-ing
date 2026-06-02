from typing import Mapping, TypedDict


class MazeConfig(TypedDict):
    """Typed normalized maze configuration."""

    WIDTH: int
    HEIGHT: int
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    SEED: int | None
    OUTPUT_FILE: str


def _require_int(config: Mapping[str, object], key: str) -> int:
    """Return a required integer setting."""
    if key not in config:
        raise ValueError(f"Missing required configuration key: {key}")
    value = config[key]
    if not isinstance(value, int):
        raise TypeError(f"{key} must be an integer.")
    return value


def _optional_point(
    config: Mapping[str, object],
    key: str,
    default: tuple[int, int],
) -> tuple[int, int]:
    """Return an optional point setting with a fallback."""
    value = config.get(key, default)
    if (
        isinstance(value, tuple)
        and len(value) == 2
        and isinstance(value[0], int)
        and isinstance(value[1], int)
    ):
        return value
    raise TypeError(f"{key} must be a tuple of two integers.")


def _optional_seed(config: Mapping[str, object]) -> int | None:
    """Return an optional seed value."""
    value = config.get("SEED")
    if value is None or isinstance(value, int):
        return value
    raise TypeError("SEED must be an integer or None.")


def _optional_output_file(config: Mapping[str, object]) -> str:
    """Return an optional output file name."""
    value = config.get("OUTPUT_FILE", "output_maze.txt")
    if isinstance(value, str):
        return value
    raise TypeError("OUTPUT_FILE must be a string.")


def parse_config(config: Mapping[str, object]) -> MazeConfig:
    """Validate and normalize a maze configuration."""
    width = _require_int(config, "WIDTH")
    height = _require_int(config, "HEIGHT")

    if width < 10 or height < 10:
        raise ValueError("The maze must be at least 10x10 in size.")

    entry = _optional_point(config, "ENTRY", (-1, -1))
    exit_pos = _optional_point(config, "EXIT", (-1, -1))

    if entry == (-1, -1):
        normalized_entry = (0, 0)
    else:
        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            raise ValueError(
                f"Entry point {entry} is out of bounds for a "
                f"{width}x{height} maze."
            )
        normalized_entry = entry

    if exit_pos == (-1, -1):
        normalized_exit = (width - 1, height - 1)
    else:
        if not (0 <= exit_pos[0] < width and 0 <= exit_pos[1] < height):
            raise ValueError(
                f"Exit point {exit_pos} is out of bounds for a "
                f"{width}x{height} maze."
            )
        normalized_exit = exit_pos

    seed = _optional_seed(config)
    output_file = _optional_output_file(config)

    return {
        "WIDTH": width,
        "HEIGHT": height,
        "ENTRY": normalized_entry,
        "EXIT": normalized_exit,
        "SEED": seed,
        "OUTPUT_FILE": output_file,
    }
