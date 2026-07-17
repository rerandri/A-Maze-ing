from collections import deque
from mazegen import MazeGenerator


class Solve_bfs:
    NORTH: int = 1
    EAST: int = 2
    SOUTH: int = 4
    WEST: int = 8

    DELTA: dict[int, tuple[int, int]] = {
        NORTH: (0, -1),
        EAST: (1, 0),
        SOUTH: (0, 1),
        WEST: (-1, 0),
    }

    def __init__(self, Maze: MazeGenerator) -> None:
        self.maze = Maze
        self._solution: list[str] = []

    def _solve_bfs(self) -> list[str]:
        queue: deque[tuple[int, int]] = deque([self.maze.entry])
        parent: dict[tuple[int, int], tuple[tuple[int, int], int]] = {
            self.maze.entry: ((-1, -1), 0)
        }

        while queue:
            x, y = queue.popleft()

            if (x, y) == self.maze.exit:
                path: list[str] = []
                curr = self.maze.exit
                while curr != self.maze.entry:
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
                return self._solution

            for direction, (dx, dy) in self.DELTA.items():
                nx, ny = x + dx, y + dy
                if (
                    self.maze._in_bounds(nx, ny)
                    and not self.maze._has_wall_internal(x, y, direction)
                    and (nx, ny) not in parent
                ):
                    parent[(nx, ny)] = ((x, y), direction)
                    queue.append((nx, ny))
        return self._solution

    def get_solution(self) -> list[str]:
        solution_path: list[str] = self._solve_bfs()
        return solution_path
