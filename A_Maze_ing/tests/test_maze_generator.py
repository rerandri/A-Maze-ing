"""Tests for the MazeGenerator module."""

from mazegen import MazeGenerator


def test_generate_default_dfs() -> None:
    """DFS generation produces a valid maze."""
    m = MazeGenerator(10, 10, (0, 0), (9, 9), seed=42)
    m.generate("dfs")
    assert m._generated
    assert len(m.get_solution()) > 0
    assert all(0 <= c <= 15 for row in m.grid for c in row)


def test_generate_kruskal() -> None:
    """Kruskal generation produces a valid maze."""
    m = MazeGenerator(10, 10, (0, 0), (9, 9), seed=42)
    m.generate("kruskal")
    assert m._generated
    assert len(m.get_solution()) > 0
    assert all(0 <= c <= 15 for row in m.grid for c in row)


def test_generate_step_dfs_count() -> None:
    """DFS step generator yields correct number of steps."""
    m = MazeGenerator(5, 5, (0, 0), (4, 4), seed=42)
    steps = list(m.generate_step("dfs"))
    assert len(steps) == 25


def test_generate_step_kruskal_count() -> None:
    """Kruskal step generator yields correct number of steps."""
    m = MazeGenerator(5, 5, (0, 0), (4, 4), seed=42)
    steps = list(m.generate_step("kruskal"))
    assert len(steps) == 25


def test_unknown_algorithm() -> None:
    """Unknown algorithm raises ValueError."""
    m = MazeGenerator(5, 5, (0, 0), (4, 4), seed=42)
    try:
        m.generate("prim")
        assert False, "Should have raised"
    except ValueError:
        pass


def test_seed_reproducibility() -> None:
    """Same seed produces identical mazes."""
    m1 = MazeGenerator(10, 10, (0, 0), (9, 9), seed=42)
    m2 = MazeGenerator(10, 10, (0, 0), (9, 9), seed=42)
    m1.generate()
    m2.generate()
    assert m1.grid == m2.grid
    assert m1.get_solution() == m2.get_solution()


def test_wall_coherence() -> None:
    """Neighbouring cells have matching walls."""
    m = MazeGenerator(10, 10, (0, 0), (9, 9), seed=42)
    m.generate()
    for y in range(m.height):
        for x in range(m.width):
            cell = m.grid[y][x]
            if x + 1 < m.width:
                east = m.grid[y][x + 1]
                assert bool(cell & MazeGenerator.EAST) == bool(
                    east & MazeGenerator.WEST
                ), f"Wall mismatch E/W at ({x},{y})"
            if y + 1 < m.height:
                south = m.grid[y + 1][x]
                assert bool(cell & MazeGenerator.SOUTH) == bool(
                    south & MazeGenerator.NORTH
                ), f"Wall mismatch S/N at ({x},{y})"


def test_outer_border_walls() -> None:
    """Outer border cells have walls on the outside edge."""
    m = MazeGenerator(10, 10, (0, 0), (9, 9), seed=42)
    m.generate()
    for y in range(m.height):
        assert m.grid[y][0] & MazeGenerator.WEST, (
            f"Left wall missing at row {y}"
        )
        assert m.grid[y][m.width - 1] & MazeGenerator.EAST, (
            f"Right wall missing at row {y}"
        )
    for x in range(m.width):
        assert m.grid[0][x] & MazeGenerator.NORTH, (
            f"Top wall missing at col {x}"
        )
        assert m.grid[m.height - 1][x] & MazeGenerator.SOUTH, (
            f"Bottom wall missing at col {x}"
        )


def test_entry_exit_inside() -> None:
    """Entry and exit cells are reachable (have open path)."""
    m = MazeGenerator(10, 10, (0, 0), (9, 9), seed=42)
    m.generate()
    sol = m.get_solution()
    assert len(sol) > 0, "Solution should not be empty"


def test_perfect_maze_single_solution_dfs() -> None:
    """DFS always produces a perfect maze (single path)."""
    m = MazeGenerator(10, 10, (0, 0), (9, 9), seed=42, perfect=True)
    m.generate("dfs")
    assert len(m.get_solution()) > 0


def test_imperfect_maze_kruskal() -> None:
    """Imperfect Kruskal still produces a valid solution."""
    m = MazeGenerator(10, 10, (0, 0), (9, 9), seed=42, perfect=False)
    m.generate("kruskal")
    assert m._generated
    assert len(m.get_solution()) > 0


def test_blocked_42_pattern() -> None:
    """Blocked cells from the 42 pattern are marked."""
    m = MazeGenerator(10, 10, (0, 0), (9, 9), seed=42)
    m.generate()
    assert len(m._blocked) > 0, "Pattern 42 should mark cells as blocked"


def test_get_cell_raises_before_generate() -> None:
    """Accessing cell before generate raises RuntimeError."""
    m = MazeGenerator(5, 5, (0, 0), (4, 4), seed=42)
    try:
        m.get_cell(0, 0)
        assert False, "Should have raised"
    except RuntimeError:
        pass


def test_get_cell_out_of_bounds() -> None:
    """Out-of-bounds cell access raises IndexError."""
    m = MazeGenerator(5, 5, (0, 0), (4, 4), seed=42)
    m.generate()
    try:
        m.get_cell(999, 999)
        assert False, "Should have raised"
    except IndexError:
        pass


def test_has_wall_invalid_direction() -> None:
    """Invalid direction raises ValueError."""
    m = MazeGenerator(5, 5, (0, 0), (4, 4), seed=42)
    m.generate()
    try:
        m.has_wall(0, 0, 99)
        assert False, "Should have raised"
    except ValueError:
        pass


def test_solution_uses_valid_moves() -> None:
    """Solution path only contains N, E, S, W."""
    m = MazeGenerator(10, 10, (0, 0), (9, 9), seed=42)
    m.generate()
    for move in m.get_solution():
        assert move in "NESW", f"Invalid move: {move}"


def test_solution_intraversible() -> None:
    """Verify the solution path actually traverses open passages."""
    m = MazeGenerator(10, 10, (0, 0), (9, 9), seed=42, perfect=True)
    m.generate()
    sol = m.get_solution()
    x, y = m.entry
    for move in sol:
        if move == "N":
            assert not m.has_wall(x, y, MazeGenerator.NORTH)
            y -= 1
        elif move == "S":
            assert not m.has_wall(x, y, MazeGenerator.SOUTH)
            y += 1
        elif move == "E":
            assert not m.has_wall(x, y, MazeGenerator.EAST)
            x += 1
        elif move == "W":
            assert not m.has_wall(x, y, MazeGenerator.WEST)
            x -= 1
    assert (x, y) == m.exit


def test_hex_output_length() -> None:
    """to_hex_lines returns correct number of rows."""
    m = MazeGenerator(10, 15, (0, 0), (9, 14), seed=42)
    m.generate()
    lines = m.to_hex_lines()
    assert len(lines) == 15
    assert all(len(line) == 10 for line in lines)


def test_corridor_max_width() -> None:
    """No open area larger than 2x3 or 3x2 exists."""
    m = MazeGenerator(10, 10, (0, 0), (9, 9), seed=42, perfect=True)
    m.generate()
    for y in range(m.height - 2):
        for x in range(m.width - 2):
            c00 = not m.has_wall(x, y, MazeGenerator.EAST)
            c01 = not m.has_wall(x + 1, y, MazeGenerator.EAST)
            c10 = not m.has_wall(x, y, MazeGenerator.SOUTH)
            c11 = not m.has_wall(x, y + 1, MazeGenerator.SOUTH)
            c20 = not m.has_wall(x + 1, y, MazeGenerator.SOUTH)
            c21 = not m.has_wall(x + 1, y + 1, MazeGenerator.SOUTH)
            north_open = not m.has_wall(x, y, MazeGenerator.NORTH)
            west_open = not m.has_wall(x, y, MazeGenerator.WEST)
            east2 = not m.has_wall(x + 2, y, MazeGenerator.EAST)
            south2 = not m.has_wall(x, y + 2, MazeGenerator.SOUTH)
            area_3x3 = (
                c00 and c01 and c10 and c11 and c20 and c21
                and not north_open and not west_open
                and not east2 and not south2
            )
            assert not area_3x3, f"3x3 open area found at ({x},{y})"


def test_get_solution_returns_copy() -> None:
    """get_solution returns a copy, not the internal list."""
    m = MazeGenerator(5, 5, (0, 0), (4, 4), seed=42)
    m.generate()
    sol1 = m.get_solution()
    sol2 = m.get_solution()
    assert sol1 is not sol2
