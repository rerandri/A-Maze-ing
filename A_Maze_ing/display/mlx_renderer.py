import importlib.util
import pathlib
import random
import sys
from typing import Optional

from mazegen import MazeGenerator

# ---------------------------------------------------------------------------
# Load the 42 MiniLibX wrapper from the local mlx.py (same directory),
# bypassing the Apple MLX package that may be installed via pip under
# the same 'mlx' name.
# ---------------------------------------------------------------------------
_MLX_PY: pathlib.Path = pathlib.Path(__file__).parent / "mlx.py"

if not _MLX_PY.exists():
    print(
        f"Error: mlx.py not found at {_MLX_PY}\n"
        "Copy mlx_CLXV/python/src/mlx/mlx.py into the display/ folder.",
        file=sys.stderr,
    )
    sys.exit(1)

_spec = importlib.util.spec_from_file_location("mlx42", _MLX_PY)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
Mlx = _mod.Mlx


# ---------------------------------------------------------------------------
# Color palette (ARGB 32-bit, 0xFF_______ = fully opaque)
# ---------------------------------------------------------------------------
class MlxColor:
    """ARGB color constants for the MLX renderer."""

    WALL_WHITE: int = 0xFF_E8E8E8
    WALL_CYAN: int = 0xFF_00C8C8
    WALL_PURPLE: int = 0xFF_9B59B6

    BACKGROUND: int = 0xFF_1A1A2E
    BLOCKED: int = 0xFF_6C3483
    PATH: int = 0xFF_2ECC71
    START: int = 0xFF_3498DB
    END: int = 0xFF_E74C3C


class MlxRenderer:
    """Render a maze in a MiniLibX graphical window.

    Args:
        maze: A fully generated MazeGenerator instance.
        cell_size: Pixel size of each maze cell (default 20).
    """

    WALL_OPTIONS: list[int] = [
        MlxColor.WALL_WHITE,
        MlxColor.WALL_CYAN,
        MlxColor.WALL_PURPLE,
    ]

    BLOCKED42_OPTIONS: list[int] = [
        MlxColor.BLOCKED,
        MlxColor.END,
        MlxColor.WALL_CYAN,
        MlxColor.PATH,
    ]

    # X11 keysym codes
    KEY_R: int = 114
    KEY_P: int = 112
    KEY_C: int = 99
    KEY_B: int = 98
    KEY_A: int = 97
    KEY_ESC: int = 65307

    ALGORITHMS: list[str] = ["dfs", "kruskal"]

    def __init__(self, maze: MazeGenerator, cell_size: int = 20) -> None:
        """Initialize the renderer.

        Args:
            maze: A fully generated MazeGenerator instance.
            cell_size: Pixel size of each maze cell.
        """
        self.maze: MazeGenerator = maze
        self.cell_size: int = cell_size
        self._color_index: int = 0
        self._blocked42_index: int = 0
        self._blocked42_color: int = self.BLOCKED42_OPTIONS[0]
        self._show_path: bool = False
        self._path_step: int = 0
        self._solution: list[str] = []
        self._curr_x: int = 0
        self._curr_y: int = 0
        self._animating: bool = False

        # Algorithm selection
        self._algorithm: str = "dfs"
        self._algo_index: int = 0

        # Generation animation state
        self._generating: bool = False
        self._gen_step_iter: object = None

        # MLX handles — set in run()
        self._mlx: Optional[object] = None
        self._mlx_ptr: Optional[object] = None
        self._win_ptr: Optional[object] = None
        self._img_ptr: Optional[object] = None
        self._img_data: Optional[memoryview] = None
        self._img_sl: int = 0

    # -----------------------------------------------------------------------
    # Geometry helpers
    # -----------------------------------------------------------------------
    @property
    def _win_width(self) -> int:
        """Pixel width of the window."""
        return (self.maze.width * 2 + 1) * self.cell_size

    @property
    def _win_height(self) -> int:
        """Pixel height of the window."""
        return (self.maze.height * 2 + 1) * self.cell_size

    # -----------------------------------------------------------------------
    # Pixel / cell drawing
    # -----------------------------------------------------------------------
    def _put_pixel(self, x: int, y: int, color: int) -> None:
        """Write one pixel directly into the image buffer.

        Args:
            x: Pixel column.
            y: Pixel row.
            color: ARGB 32-bit color value.
        """
        if self._img_data is None:
            return
        offset: int = y * self._img_sl + x * 4
        if offset + 3 >= len(self._img_data):
            return
        self._img_data[offset:offset + 4] = color.to_bytes(4, 'little')

    def _fill_cell(self, grid_x: int, grid_y: int, color: int) -> None:
        """Fill a cell_size x cell_size block in the image buffer.

        Args:
            grid_x: Cell column in the pixel grid.
            grid_y: Cell row in the pixel grid.
            color: ARGB 32-bit color value.
        """
        px: int = grid_x * self.cell_size
        py: int = grid_y * self.cell_size
        for dy in range(self.cell_size):
            for dx in range(self.cell_size):
                self._put_pixel(px + dx, py + dy, color)

    # -----------------------------------------------------------------------
    # Maze drawing
    # -----------------------------------------------------------------------
    def _draw_maze(self) -> None:
        """Redraw the full maze into the image buffer."""
        wall_color: int = self.WALL_OPTIONS[self._color_index]
        cols: int = self.maze.width * 2 + 1
        rows: int = self.maze.height * 2 + 1

        for row in range(rows):
            for col in range(cols):
                self._fill_cell(col, row, wall_color)

        for y in range(self.maze.height):
            for x in range(self.maze.width):
                cell_color: int = (
                    self._blocked42_color
                    if (x, y) in self.maze._blocked
                    else MlxColor.BACKGROUND
                )
                self._fill_cell(2 * x + 1, 2 * y + 1, cell_color)

                if not self.maze.has_wall(x, y, MazeGenerator.NORTH):
                    self._fill_cell(2 * x + 1, 2 * y, MlxColor.BACKGROUND)
                if not self.maze.has_wall(x, y, MazeGenerator.SOUTH):
                    self._fill_cell(2 * x + 1, 2 * y + 2, MlxColor.BACKGROUND)
                if not self.maze.has_wall(x, y, MazeGenerator.EAST):
                    self._fill_cell(2 * x + 2, 2 * y + 1, MlxColor.BACKGROUND)
                if not self.maze.has_wall(x, y, MazeGenerator.WEST):
                    self._fill_cell(2 * x, 2 * y + 1, MlxColor.BACKGROUND)

        ex, ey = self.maze.entry
        xx, xy = self.maze.exit
        self._fill_cell(2 * ex + 1, 2 * ey + 1, MlxColor.START)
        self._fill_cell(2 * xx + 1, 2 * xy + 1, MlxColor.END)

    def _draw_path_step(self) -> None:
        """Advance the solution path animation by one step.

        Called every frame by mlx_loop_hook while _animating is True.
        """
        if self._path_step >= len(self._solution):
            xx, xy = self.maze.exit
            self._fill_cell(2 * xx + 1, 2 * xy + 1, MlxColor.END)
            self._animating = False
            self._flush()
            return

        move: str = self._solution[self._path_step]
        cx: int = self._curr_x
        cy: int = self._curr_y

        if move == 'N':
            self._fill_cell(2 * cx + 1, 2 * cy, MlxColor.PATH)
            self._curr_y -= 1
        elif move == 'S':
            self._fill_cell(2 * cx + 1, 2 * cy + 2, MlxColor.PATH)
            self._curr_y += 1
        elif move == 'E':
            self._fill_cell(2 * cx + 2, 2 * cy + 1, MlxColor.PATH)
            self._curr_x += 1
        elif move == 'W':
            self._fill_cell(2 * cx, 2 * cy + 1, MlxColor.PATH)
            self._curr_x -= 1

        self._fill_cell(
            2 * self._curr_x + 1,
            2 * self._curr_y + 1,
            MlxColor.PATH,
        )
        self._path_step += 1
        self._flush()

    def _draw_from_grid(self, grid: list[list[int]]) -> None:
        """Draw the maze from a raw grid snapshot (for generation animation).

        Args:
            grid: A 2D list of wall bitmasks, same format as self.maze.grid.
        """
        wall_color: int = self.WALL_OPTIONS[self._color_index]
        cols: int = self.maze.width * 2 + 1
        rows: int = self.maze.height * 2 + 1

        for row in range(rows):
            for col in range(cols):
                self._fill_cell(col, row, wall_color)

        for y in range(self.maze.height):
            for x in range(self.maze.width):
                is_blocked = (x, y) in self.maze._blocked
                cell_color = (
                    self._blocked42_color if is_blocked
                    else MlxColor.BACKGROUND
                )
                self._fill_cell(2 * x + 1, 2 * y + 1, cell_color)

                cell = grid[y][x]
                if not (cell & MazeGenerator.NORTH):
                    self._fill_cell(2 * x + 1, 2 * y, MlxColor.BACKGROUND)
                if not (cell & MazeGenerator.SOUTH):
                    self._fill_cell(2 * x + 1, 2 * y + 2, MlxColor.BACKGROUND)
                if not (cell & MazeGenerator.EAST):
                    self._fill_cell(2 * x + 2, 2 * y + 1, MlxColor.BACKGROUND)
                if not (cell & MazeGenerator.WEST):
                    self._fill_cell(2 * x, 2 * y + 1, MlxColor.BACKGROUND)

        ex, ey = self.maze.entry
        xx, xy = self.maze.exit
        self._fill_cell(2 * ex + 1, 2 * ey + 1, MlxColor.START)
        self._fill_cell(2 * xx + 1, 2 * xy + 1, MlxColor.END)

    def _start_generation(self) -> None:
        """Begin animated maze generation using generate_step()."""
        self.maze._generated = False
        self._animating = False
        self._generating = True
        try:
            self._gen_step_iter = self.maze.generate_step(self._algorithm)
        except Exception as exc:
            print(f"Generation error: {exc}", file=sys.stderr)
            self._generating = False
            self._gen_step_iter = None

    def _advance_generation(self) -> None:
        """Advance generation animation by one step."""
        if self._gen_step_iter is None:
            self._generating = False
            return
        try:
            grid_snapshot = next(self._gen_step_iter)
            self._draw_from_grid(grid_snapshot)
            self._flush()
        except StopIteration:
            self._generating = False
            self._gen_step_iter = None
            self.maze._generated = True
            self._refresh()
        except Exception as exc:
            print(f"Generation animation error: {exc}", file=sys.stderr)
            self._generating = False
            self._gen_step_iter = None
            self.maze._generated = True
            self._refresh()

    def _flush(self) -> None:
        """Push the image buffer to the window."""
        if self._mlx and self._mlx_ptr and self._win_ptr and self._img_ptr:
            self._mlx.mlx_put_image_to_window(
                self._mlx_ptr, self._win_ptr, self._img_ptr, 0, 0
            )

    def _refresh(self) -> None:
        """Redraw maze and restart path animation if enabled."""
        self._draw_maze()
        self._flush()
        if self._show_path:
            self._solution = self.maze.get_solution()
            ex, ey = self.maze.entry
            self._curr_x = ex
            self._curr_y = ey
            self._path_step = 0
            self._animating = True

    # -----------------------------------------------------------------------
    # Event callbacks
    # -----------------------------------------------------------------------
    def _on_key(self, keycode: int, param: object) -> None:
        """Handle keyboard input.

        Args:
            keycode: X11 keysym code.
            param: Unused parameter required by the MLX API.
        """
        if keycode == self.KEY_ESC:
            self._cleanup()
            sys.exit(0)

        elif keycode == self.KEY_R:
            self.maze.seed = random.randint(0, 2 ** 32)
            self.maze.entry = (
                random.randint(0, self.maze.width - 1),
                random.randint(0, self.maze.height - 1),
            )
            self.maze.exit = (
                random.randint(0, self.maze.width - 1),
                random.randint(0, self.maze.height - 1),
            )
            self._start_generation()

        elif keycode == self.KEY_A:
            self._algo_index = (self._algo_index + 1) % len(self.ALGORITHMS)
            self._algorithm = self.ALGORITHMS[self._algo_index]
            print(f" Algorithm: {self._algorithm}")
            self._start_generation()

        elif keycode == self.KEY_P:
            self._show_path = not self._show_path
            self._refresh()

        elif keycode == self.KEY_C:
            self._color_index = (
                self._color_index + 1
            ) % len(self.WALL_OPTIONS)
            self._refresh()

        elif keycode == self.KEY_B:
            self._blocked42_index = (
                self._blocked42_index + 1
            ) % len(self.BLOCKED42_OPTIONS)
            self._blocked42_color = self.BLOCKED42_OPTIONS[
                self._blocked42_index
            ]
            self._refresh()

    def _on_loop(self, param: object) -> None:
        """Advance path animation each frame.

        Args:
            param: Unused parameter required by the MLX API.
        """
        if self._generating:
            self._advance_generation()
        elif self._animating:
            self._draw_path_step()

    def _on_close(self, param: object) -> None:
        """Handle window close (WM_DELETE_WINDOW event 33).

        Args:
            param: Unused parameter required by the MLX API.
        """
        self._cleanup()
        sys.exit(0)

    # -----------------------------------------------------------------------
    # Resource management
    # -----------------------------------------------------------------------
    def _cleanup(self) -> None:
        """Destroy MLX resources in the correct order."""
        if not self._mlx or not self._mlx_ptr:
            return
        try:
            if self._img_ptr:
                self._mlx.mlx_destroy_image(self._mlx_ptr, self._img_ptr)
            if self._win_ptr:
                self._mlx.mlx_destroy_window(self._mlx_ptr, self._win_ptr)
            self._mlx.mlx_release(self._mlx_ptr)
        except Exception as e:
            print(f"Warning: cleanup error: {e}", file=sys.stderr)

    # -----------------------------------------------------------------------
    # Entry point
    # -----------------------------------------------------------------------
    def run(self) -> None:
        """Open the MLX window and start the event loop.

        Blocks until ESC is pressed or the window is closed.
        Note: Ctrl+C does NOT interrupt mlx_loop — use ESC or Ctrl+\\.
        """
        try:
            self._mlx = Mlx()
        except Exception as e:
            print(f"Error: cannot initialize MLX: {e}", file=sys.stderr)
            sys.exit(1)

        self._mlx_ptr = self._mlx.mlx_init()
        if not self._mlx_ptr:
            print("Error: mlx_init() failed.", file=sys.stderr)
            sys.exit(1)

        self._win_ptr = self._mlx.mlx_new_window(
            self._mlx_ptr,
            self._win_width,
            self._win_height,
            "A-Maze-ing",
        )
        if not self._win_ptr:
            print("Error: mlx_new_window() failed.", file=sys.stderr)
            sys.exit(1)

        self._img_ptr = self._mlx.mlx_new_image(
            self._mlx_ptr, self._win_width, self._win_height
        )
        if not self._img_ptr:
            print("Error: mlx_new_image() failed.", file=sys.stderr)
            sys.exit(1)

        self._img_data, _bpp, self._img_sl, _fmt = (
            self._mlx.mlx_get_data_addr(self._img_ptr)
        )

        self._mlx.mlx_key_hook(self._win_ptr, self._on_key, None)
        self._mlx.mlx_loop_hook(self._mlx_ptr, self._on_loop, None)
        self._mlx.mlx_hook(self._win_ptr, 33, 0, self._on_close, None)

        self._refresh()

        print("=== A-Maze-ing (MLX) ===")
        print(f"  R   - re-generate maze (algo: {self._algorithm})")
        print("  A   - switch algorithm (dfs/kruskal)")
        print("  P   - toggle path")
        print("  C   - cycle wall colors")
        print("  B   - cycle '42' pattern colors")
        print("  ESC - quit  |  Ctrl+\\ - force kill")

        self._mlx.mlx_loop(self._mlx_ptr)
