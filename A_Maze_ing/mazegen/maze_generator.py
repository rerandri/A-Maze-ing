from collections import deque
import random
import sys
from typing import Generator


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

    def get_solution(self) -> list[str]:
        """Return a copy of the current solution path."""
        self._require_generated()
        return list(self._solution)

    def to_hex_lines(self) -> list[str]:
        """Serialize the maze grid into hexadecimal text lines."""
        self._require_generated()
        return ["".join(f"{cell:X}" for cell in row) for row in self.grid]

    def generate(self, algorithm: str = "dfs") -> None:
        """Generate maze structure and compute the shortest solution path.

        Args:
            algorithm: Generation algorithm to use ("dfs" or "kruskal").

        If perfect is False, extra walls are removed after generation to create
        loops and alternative paths (imperfect maze).
        """
        self._init_grid()
        random.seed(self.seed)
        self._carve_pattern42()
        if algorithm == "dfs":
            self._generate_dfs()
        elif algorithm == "kruskal":
            self._generate_kruskal()
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        if not self.perfect:
            self._add_extra_passages()
        self._solve_bfs()
        self._generated = True

    def generate_step(self, algorithm: str = "dfs"
                      ) -> Generator[list[list[int]], None, None]:
        """Generator that yields a grid copy after each wall removal.

        Each yielded value is a deep copy of self.grid, suitable for
        animating the maze-building process step by step.

        Args:
            algorithm: Generation algorithm ("dfs" or "kruskal").

        Yields:
            A snapshot of the grid after each wall removal.
        """
        self._init_grid()
        random.seed(self.seed)
        self._carve_pattern42()
        yield self._grid_copy()
        if algorithm == "dfs":
            yield from self._generate_dfs_step()
        elif algorithm == "kruskal":
            yield from self._generate_kruskal_step()
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        if not self.perfect:
            self._add_extra_passages()
            yield self._grid_copy()
        self._solve_bfs()
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

    def _generate_dfs_step(self) -> Generator[list[list[int]], None, None]:
        """DFS generator that yields after each wall removal."""
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
                yield self._grid_copy()
            else:
                stack.pop()

    def _add_extra_passages(self) -> None:
        """Remove additional walls to create loops (imperfect maze).

        For each cell, with 50% probability, remove a wall to a random neighbor
        if that wall is still present and the neighbor is not blocked.
        """
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
                        break  # un seul mur supprimé par cellule

    def _generate_kruskal(self) -> None:
        """Generate passages using Kruskal's algorithm.

        Lists all walls between adjacent cells, shuffles them randomly,
        then removes each wall if its two cells belong to different
        connected components (union-find).  This produces a perfect maze
        (spanning tree).
        """
        edges: list[tuple[int, int, int, int, int, int]] = []
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self._blocked:
                    continue
                if x + 1 < self.width and (x + 1, y) not in self._blocked:
                    edges.append((x, y, self.EAST, x + 1, y, self.WEST))
                if y + 1 < self.height and (x, y + 1) not in self._blocked:
                    edges.append((x, y, self.SOUTH, x, y + 1, self.NORTH))

        random.shuffle(edges)

        parent: dict[tuple[int, int], tuple[int, int]] = {}
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in self._blocked:
                    parent[(x, y)] = (x, y)

        def _find(p: tuple[int, int]) -> tuple[int, int]:
            while parent[p] != p:
                parent[p] = parent[parent[p]]
                p = parent[p]
            return p

        def _union(a: tuple[int, int], b: tuple[int, int]) -> None:
            ra, rb = _find(a), _find(b)
            if ra != rb:
                parent[rb] = ra

        for x1, y1, d1, x2, y2, d2 in edges:
            if _find((x1, y1)) != _find((x2, y2)):
                self._remove_wall(x1, y1, d1, x2, y2, d2)
                _union((x1, y1), (x2, y2))

    def _generate_kruskal_step(
        self,
    ) -> Generator[list[list[int]], None, None]:
        """Kruskal generator that yields after each wall removal."""
        edges: list[tuple[int, int, int, int, int, int]] = []
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self._blocked:
                    continue
                if x + 1 < self.width and (x + 1, y) not in self._blocked:
                    edges.append((x, y, self.EAST, x + 1, y, self.WEST))
                if y + 1 < self.height and (x, y + 1) not in self._blocked:
                    edges.append((x, y, self.SOUTH, x, y + 1, self.NORTH))

        random.shuffle(edges)

        parent: dict[tuple[int, int], tuple[int, int]] = {}
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in self._blocked:
                    parent[(x, y)] = (x, y)

        def _find(p: tuple[int, int]) -> tuple[int, int]:
            while parent[p] != p:
                parent[p] = parent[parent[p]]
                p = parent[p]
            return p

        def _union(a: tuple[int, int], b: tuple[int, int]) -> None:
            ra, rb = _find(a), _find(b)
            if ra != rb:
                parent[rb] = ra

        for x1, y1, d1, x2, y2, d2 in edges:
            if _find((x1, y1)) != _find((x2, y2)):
                self._remove_wall(x1, y1, d1, x2, y2, d2)
                _union((x1, y1), (x2, y2))
                yield self._grid_copy()

    def _solve_bfs(self) -> None:
        """Find the shortest path from entry to exit using BFS."""
        self._solution = []

        queue: deque[tuple[int, int]] = deque([self.entry])
        parent: dict[tuple[int, int], tuple[tuple[int, int], int]] = {
            self.entry: ((-1, -1), 0)}

        while queue:
            x, y = queue.popleft()

            if (x, y) == self.exit:
                path: list[str] = []
                curr = self.exit
                while curr != self.entry:
                    prev, direction = parent[curr]
                    direction_names = {
                        self.NORTH: "N",
                        self.SOUTH: "S",
                        self.EAST: "E",
                        self.WEST: "W"
                    }
                    path.append(direction_names.get(direction, "_"))
                    curr = prev
                path.reverse()
                self._solution = path
                return

            for direction, (dx, dy) in self.DELTA.items():
                nx, ny = x + dx, y + dy
                if (
                    self._in_bounds(nx, ny)
                    and not self._has_wall_internal(x, y, direction)
                    and (nx, ny) not in parent
                ):
                    parent[(nx, ny)] = ((x, y), direction)
                    queue.append((nx, ny))
