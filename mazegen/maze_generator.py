import random
import sys


class MazeGenerator:
    NORTH: int = 1
    EAST: int = 2
    SOUTH: int = 4
    WEST: int = 8

    PATTERN_42: list[str] = [
        "F000FFF",
        "F00000F",
        "FFF0FFF",
        "00F0F00",
        "00F0FFF",
    ]

    OPPOSITE: dict[int, int] = {
        NORTH: SOUTH,
        SOUTH: NORTH,
        EAST: WEST,
        WEST: EAST,
    }

    DELTA: dict[int, tuple[int, int]] = {
        NORTH: (0, -1),
        EAST: (1, 0),
        SOUTH: (0, 1),
        WEST: (-1, 0),
    }

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
        seed: int | None = None,
        perfect: bool = True,
    ) -> None:
        self.width: int = width
        self.height: int = height
        self.entry: tuple[int, int] = entry
        self.exit: tuple[int, int] = exit
        self._blocked: set[tuple[int, int]] = set()
        self.seed: int = seed if seed is not None else random.randint(0, 2**31)
        self.perfect: bool = perfect
        self.grid: list[list[int]] = []
        self._solution: list[str] = []
        self._generated: bool = False

    def _init_grid(self) -> None:
        """Initialize the grid with all walls closed."""
        closed: int = self.NORTH | self.SOUTH | self.EAST | self.WEST
        self.grid = [[closed for _ in range(self.width)]
                     for _ in range(self.height)]

    def _grid_copy(self) -> list[list[int]]:
        """Return a deep copy of the current grid."""
        return [row[:] for row in self.grid]

    def _remove_wall(
        self,
        x1: int, y1: int, wto_open1: int,
        x2: int, y2: int, wto_open2: int
    ) -> None:
        """Remove walls between two adjacent cells."""
        self.grid[y1][x1] &= ~wto_open1
        self.grid[y2][x2] &= ~wto_open2

    def _in_bounds(self, x: int, y: int) -> bool:
        """Return whether coordinates are inside maze bounds."""
        return 0 <= x < self.width and 0 <= y < self.height

    def _require_generated(self) -> None:
        """Raise when maze data is accessed before generation."""
        if not self._generated:
            raise RuntimeError(
                "Maze not generated yet. Call generate() first."
            )

    def get_cell(self, x: int, y: int) -> int:
        """Return the wall bitmask for the cell at given coordinates."""
        self._require_generated()
        if not self._in_bounds(x, y):
            raise IndexError(f"Cell coordinates out of bounds: ({x}, {y})")
        return self.grid[y][x]

    def has_wall(self, x: int, y: int, direction: int) -> bool:
        """Return whether a wall exists in `direction` for cell `(x, y)`."""
        if direction not in self.DELTA:
            raise ValueError(f"Invalid direction: {direction}")
        cell: int = self.get_cell(x, y)
        return (cell & direction) != 0

    def _has_wall_internal(self, x: int, y: int, direction: int) -> bool:
        """Check a wall without requiring generated-state validation."""
        if not self._in_bounds(x, y):
            return True
        return (self.grid[y][x] & direction) != 0

    def to_hex_lines(self) -> list[str]:
        """Serialize the maze grid into hexadecimal text lines."""
        self._require_generated()
        return ["".join(f"{cell:X}" for cell in row) for row in self.grid]

    def generate(self) -> None:
        """Generate maze structure and compute the shortest solution path."""
        self._init_grid()
        random.seed(self.seed)
        self._carve_pattern42()
        self._generate_dfs()
        if not self.perfect:
            self._add_extra_passages()
        self._generated = True

    def _carve_pattern42(self) -> None:
        """Mark blocked cells to draw the embedded '42' pattern."""
        pattern_height = len(self.PATTERN_42)
        if pattern_height == 0:
            return
        pattern_width = len(self.PATTERN_42[0])

        if self.width < pattern_width or self.height < pattern_height:
            print(
                "Maze is too small to draw the '42' pattern.",
                file=sys.stderr,
            )
            return

        start_x = (self.width - pattern_width) // 2
        start_y = (self.height - pattern_height) // 2
        for r, row_str in enumerate(self.PATTERN_42):
            for c, hex_char in enumerate(row_str):
                if hex_char == "F":
                    y = start_y + r
                    x = start_x + c
                    if self._in_bounds(x, y):
                        self._blocked.add((x, y))

    def _generate_dfs(self) -> None:
        """Generate passages using recursive-backtracker DFS."""
        stack: list[tuple[int, int]] = [self.entry]
        visited: set[tuple[int, int]] = {self.entry}

        while stack:
            current_x, current_y = stack[-1]
            neighbors = []
            for direction, (dx, dy) in self.DELTA.items():
                nx = current_x + dx
                ny = current_y + dy
                if (
                    self._in_bounds(nx, ny)
                    and (nx, ny) not in visited
                    and (nx, ny) not in self._blocked
                ):
                    neighbors.append((nx, ny, direction))

            if neighbors:
                next_x, next_y, direction = random.choice(neighbors)
                self._remove_wall(
                    current_x,
                    current_y,
                    direction,
                    next_x,
                    next_y,
                    self.OPPOSITE[direction]
                )
                visited.add((next_x, next_y))
                stack.append((next_x, next_y))
            else:
                stack.pop()

    def _add_extra_passages(self) -> None:
        """Remove additional walls to create loops (imperfect maze)."""
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self._blocked:
                    continue
                directions = list(self.DELTA.items())
                random.shuffle(directions)
                for direction, (dx, dy) in directions:
                    nx, ny = x + dx, y + dy
                    if (
                        self._in_bounds(nx, ny)
                        and (nx, ny) not in self._blocked
                        and self._has_wall_internal(x, y, direction)
                        and random.random() < 0.5
                    ):
                        self._remove_wall(
                            x, y, direction,
                            nx, ny, self.OPPOSITE[direction],
                        )
                    break
