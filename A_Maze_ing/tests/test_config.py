"""Tests for config parsing and validation."""

import io

import pytest

from mazegen import parse_config, read_config_file


def _cfg(**kw: object) -> dict[str, object]:
    return kw


def test_minimal_config() -> None:
    """Minimum valid config."""
    cfg = _cfg(WIDTH=10, HEIGHT=10, ENTRY=(0, 0), EXIT=(9, 9), PERFECT=True)
    parsed = parse_config(cfg)
    assert parsed["WIDTH"] == 10
    assert parsed["HEIGHT"] == 10
    assert parsed["ENTRY"] == (0, 0)
    assert parsed["EXIT"] == (9, 9)
    assert parsed["PERFECT"] is True
    assert parsed["OUTPUT_FILE"] == "output_maze.txt"


def test_missing_width() -> None:
    """Missing WIDTH raises ValueError."""
    with pytest.raises((ValueError, KeyError)):
        parse_config(_cfg(HEIGHT=10, ENTRY=(0, 0), EXIT=(9, 9), PERFECT=True))


def test_small_maze_raises() -> None:
    """Maze smaller than 10x10 raises ValueError."""
    with pytest.raises(ValueError, match="at least 10x10"):
        parse_config(
            _cfg(WIDTH=5, HEIGHT=5, ENTRY=(0, 0), EXIT=(4, 4), PERFECT=True)
        )


def test_entry_exit_same_raises() -> None:
    """Identical entry/exit raises ValueError."""
    with pytest.raises(ValueError, match="must be different"):
        parse_config(
            _cfg(WIDTH=10, HEIGHT=10, ENTRY=(0, 0), EXIT=(0, 0), PERFECT=True)
        )


def test_entry_out_of_bounds() -> None:
    """Entry outside maze bounds raises ValueError."""
    with pytest.raises(ValueError, match="out of bounds"):
        parse_config(
            _cfg(
                WIDTH=10, HEIGHT=10,
                ENTRY=(99, 99), EXIT=(9, 9),
                PERFECT=True,
            )
        )


def test_exit_out_of_bounds() -> None:
    """Exit outside maze bounds raises ValueError."""
    with pytest.raises(ValueError, match="out of bounds"):
        parse_config(
            _cfg(
                WIDTH=10, HEIGHT=10,
                ENTRY=(0, 0), EXIT=(99, 99),
                PERFECT=True,
            )
        )


def test_perfect_false() -> None:
    """PERFECT=False is accepted."""
    cfg = _cfg(WIDTH=10, HEIGHT=10, ENTRY=(0, 0), EXIT=(9, 9), PERFECT=False)
    parsed = parse_config(cfg)
    assert parsed["PERFECT"] is False


def test_custom_seed() -> None:
    """Custom integer seed is accepted."""
    cfg = _cfg(WIDTH=10, HEIGHT=10, ENTRY=(0, 0),
               EXIT=(9, 9), SEED=123, PERFECT=True)
    parsed = parse_config(cfg)
    assert parsed["SEED"] == 123


def test_custom_output_file() -> None:
    """Custom OUTPUT_FILE is accepted."""
    cfg = _cfg(
        WIDTH=10, HEIGHT=10, ENTRY=(0, 0), EXIT=(9, 9),
        PERFECT=True, OUTPUT_FILE="test.txt",
    )
    parsed = parse_config(cfg)
    assert parsed["OUTPUT_FILE"] == "test.txt"


def test_read_config_comments() -> None:
    """Lines starting with # are ignored."""
    text = (
        "# This is a comment\n"
        "WIDTH=10\n"
        "# Another comment\n"
        "HEIGHT=10\n"
        "ENTRY=0,0\n"
        "EXIT=9,9\n"
        "PERFECT=True\n"
    )
    raw = read_config_file(io.StringIO(text))
    assert "WIDTH" in raw
    assert "HEIGHT" in raw
    assert "PERFECT" in raw


def test_read_config_perfect_boolean() -> None:
    """PERFECT=True is parsed as boolean."""
    text = "WIDTH=10\nHEIGHT=10\nENTRY=0,0\nEXIT=9,9\nPERFECT=True\n"
    raw = read_config_file(io.StringIO(text))
    parsed = parse_config(raw)
    assert parsed["PERFECT"] is True


def test_read_config_perfect_false() -> None:
    """PERFECT=False is parsed as boolean."""
    text = "WIDTH=10\nHEIGHT=10\nENTRY=0,0\nEXIT=9,9\nPERFECT=False\n"
    raw = read_config_file(io.StringIO(text))
    parsed = parse_config(raw)
    assert parsed["PERFECT"] is False


def test_read_config_invalid_perfect() -> None:
    """Invalid PERFECT value raises ValueError."""
    text = "WIDTH=10\nHEIGHT=10\nENTRY=0,0\nEXIT=9,9\nPERFECT=maybe\n"
    with pytest.raises(ValueError, match="Invalid boolean"):
        read_config_file(io.StringIO(text))
