from typing import Mapping, TypedDict


class MazeConfig(TypedDict):
    WIDTH: int
    HEIGHT: int
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    SEED: int | None
    PERFECT: bool
    OUTPUT_FILE: str


def _require_int(config: Mapping[str, object], key: str) -> int:
    if key not in config:
        raise ValueError(f"Missing required configuration key: '{key}'")
    value = config[key]
    if not isinstance(value, int):
        raise TypeError(
            f"'{key}' must be an integer,"
            f" got {type(value).__name__}."
        )
    return value


def _optional_point(
    config: Mapping[str, object],
    key: str,
    default: tuple[int, int],
) -> tuple[int, int]:
    value = config.get(key, default)
    if (
        isinstance(value, tuple)
        and len(value) == 2
        and isinstance(value[0], int)
        and isinstance(value[1], int)
    ):
        return value
    raise TypeError(
        f"'{key}' must be a tuple of two integers,"
        f" got {value!r}."
    )


def _optional_seed(config: Mapping[str, object]) -> int | None:
    value = config.get("SEED")
    if value is None or isinstance(value, int):
        return value
    raise TypeError(
        f"SEED must be an integer or None,"
        f" got {type(value).__name__}."
    )


def _optional_output_file(config: Mapping[str, object]) -> str:
    value = config.get("OUTPUT_FILE", "output_maze.txt")
    if isinstance(value, str):
        return value
    raise TypeError(
        f"OUTPUT_FILE must be a string,"
        f" got {type(value).__name__}."
    )


def parse_config(config: Mapping[str, object]) -> MazeConfig:
    width = _require_int(config, "WIDTH")
    height = _require_int(config, "HEIGHT")

    if width < 10 or height < 10:
        raise ValueError(
            f"Maze too small: got {width}x{height},"
            f" minimum is 10x10."
        )

    entry = _optional_point(config, "ENTRY", (-1, -1))
    exit_pos = _optional_point(config, "EXIT", (-1, -1))

    if entry == (-1, -1):
        normalized_entry = (0, 0)
    else:
        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            raise ValueError(
                f"Entry point {entry} is out of bounds"
                f" for a {width}x{height} maze."
            )
        normalized_entry = entry

    if exit_pos == (-1, -1):
        normalized_exit = (width - 1, height - 1)
    else:
        if not (0 <= exit_pos[0] < width and 0 <= exit_pos[1] < height):
            raise ValueError(
                f"Exit point {exit_pos} is out of bounds"
                f" for a {width}x{height} maze."
            )
        normalized_exit = exit_pos

    seed = _optional_seed(config)
    output_file = _optional_output_file(config)
    perfect = config.get("PERFECT", True)
    if not isinstance(perfect, bool):
        raise TypeError(
            f"PERFECT must be a boolean,"
            f" got {type(perfect).__name__}."
        )

    if normalized_entry == normalized_exit:
        raise ValueError(
            f"Entry and exit cannot be the same cell:"
            f" both at {normalized_entry}."
        )

    return {
        "WIDTH": width,
        "HEIGHT": height,
        "ENTRY": normalized_entry,
        "EXIT": normalized_exit,
        "SEED": seed,
        "PERFECT": perfect,
        "OUTPUT_FILE": output_file,
    }
