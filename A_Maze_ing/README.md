*This project has been created as part of the 42 curriculum by Rirandri and Rirazafi.*

## Description

A-Maze-ing is a maze generator and visualizer written in Python 3. It reads a configuration file, generates a maze using the **recursive backtracker** (DFS-based) algorithm, writes the result to an output file in hexadecimal format, and displays the maze either in the terminal (ASCII with ANSI colors) or in a graphical window (via MiniLibX).

Key features:
- Random maze generation with reproducible seeds
- Embedded "42" pattern made of blocked cells
- Perfect maze mode (single path between entry and exit)
- Imperfect maze mode (loops and alternative paths)
- Shortest path calculation using BFS
- Terminal rendering with ANSI colors
- Graphical rendering with MiniLibX
- Interactive controls: regenerate, show/hide path, cycle colors

## Instructions

### Dependencies

- Python 3.10 or later
- flake8 (for linting)
- mypy (for static type checking)
- build (for package building)
- MiniLibX library (for graphical rendering only)

### Installation

```bash
make install
```

Or manually:

```bash
pip3 install flake8 mypy build
```

### Execution

```bash
make run
```

Or manually:

```bash
python3 a_maze_ing.py config.txt
```

You will be prompted to choose between Terminal (ASCII) and Graphical (MLX) rendering.

### Debug mode

```bash
make debug
```

### Linting

```bash
make lint        # flake8 + mypy
make lint-strict # flake8 + mypy --strict
```

### Build the reusable package

```bash
make build
```

The mazegen package will be built as `.tar.gz` and `.whl` in the `dist/` directory.

### Clean

```bash
make clean
```

## Configuration file format

The configuration file uses `KEY=VALUE` pairs, one per line. Lines starting with `#` are ignored.

| Key | Description | Example |
|-----|-------------|---------|
| `WIDTH` | Maze width (number of cells) | `WIDTH=20` |
| `HEIGHT` | Maze height (number of cells) | `HEIGHT=15` |
| `ENTRY` | Entry coordinates `x,y` | `ENTRY=0,0` |
| `EXIT` | Exit coordinates `x,y` | `EXIT=19,14` |
| `OUTPUT_FILE` | Output filename | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Whether the maze is perfect (single path) | `PERFECT=True` |
| `SEED` | Random seed (optional) | `SEED=42` |

A default `config.txt` is provided in the repository.

### Example

```
WIDTH=30
HEIGHT=30
ENTRY=1,1
EXIT=19,19
SEED=0
OUTPUT_FILE=maze.txt
PERFECT=True
```

## Maze generation algorithm

We chose the **recursive backtracker** (iterative DFS) algorithm because:

- It guarantees a **perfect maze** (exactly one path between any two cells), which maps directly to a spanning tree in graph theory.
- It is simple to implement and efficient (O(n) time and space).
- It naturally produces mazes with narrow corridors (1 cell wide), satisfying the project constraint that corridors cannot be wider than 2 cells.
- The iterative version (using an explicit stack) avoids Python's recursion limit.

The algorithm:
1. Start from the entry cell, mark it visited.
2. While there is a cell on the stack:
   - Pick a random unvisited neighbour, remove the wall between them, mark it visited, push it.
   - If no unvisited neighbour exists, backtrack (pop the stack).
3. After the DFS, the shortest path from entry to exit is computed using **BFS** (breadth-first search), which guarantees the shortest path in an unweighted grid.

If `PERFECT=False`, additional walls are randomly removed after generation to create loops and alternative paths.

## Output file format

The maze is saved as hexadecimal digits, one row per line. Each hexadecimal digit encodes the closed walls of a cell using the following bit layout:

| Bit | Direction |
|-----|-----------|
| 0 (LSB) | North |
| 1 | East |
| 2 | South |
| 3 | West |

A bit value of `1` means the wall is closed (present), `0` means open (absent).

After an empty line, the output file contains:
1. Entry coordinates (`x,y`)
2. Exit coordinates (`x,y`)
3. The shortest path from entry to exit using the letters `N`, `E`, `S`, `W`

### Example

```
D5151555395395551555553D513953
97C3A953AABC4557A95553C556AABA

1,1
19,19
EESSWNWN...
```

## Reusable code

The `mazegen` module (`A_Maze_ing/mazegen/`) is a standalone Python package that can be installed independently via pip:

```bash
pip3 install dist/mazegen-1.0.0-py3-none-any.whl
```

### Usage example

```python
from mazegen import MazeGenerator

maze = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit=(19, 14),
    seed=42,
    perfect=True,
)
maze.generate()

# Access the solution
solution = maze.get_solution()  # list of "N", "E", "S", "W"

# Check walls
has_north_wall = maze.has_wall(5, 3, MazeGenerator.NORTH)

# Export to hex
hex_lines = maze.to_hex_lines()
```

The module provides:
- `MazeGenerator` — the maze generation class
- `parse_config` — configuration parser
- `read_config_file` — raw config file reader
- Type-safe configuration via `MazeConfig` TypedDict

## Visual representation

### Terminal (ASCII) mode

Renders the maze using ANSI escape codes with colored blocks:
- Walls: white/cyan/purple (cycle with option 4)
- Background (path): dark blue
- Blocked cells (42 pattern): purple
- Path: green
- Entry: blue
- Exit: red

User interactions (menu-driven):
1. Re-generate a new maze
2. Display maze
3. Show/Hide path
4. Rotate maze colors
5. Quit

### Graphical (MLX) mode

Renders the maze in a window using the MiniLibX library:
- Walls: white/cyan/purple (cycle with C key)
- Background: dark blue
- Path: green
- Entry: blue
- Exit: red

User interactions (keyboard):
- R — re-generate maze
- P — toggle path animation
- C — cycle wall colors
- ESC — quit

## Resources

### Documentation
- [Python typing module](https://docs.python.org/3/library/typing.html)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)
- [flake8 — Style Guide](https://flake8.pycqa.org/)

### Maze generation
- [Jamis Buck — Maze Algorithms](https://www.jamisbuck.org/mazes/)
- [Wikipedia — Maze generation algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive backtracker (DFS)](https://en.wikipedia.org/wiki/Maze_generation_algorithm#Iterative_implementation)

### MiniLibX
- [42 MiniLibX documentation](https://harm-smits.github.io/42docs/libs/minilibx)

### AI usage

AI was used for the following tasks:
- Generating the initial structure of the renderer and MLX wrapper.
- Debugging terminal rendering bugs (duplicate lines on small terminals, scroll issues).
- Writing documentation (this README, Explanation_MLX.md, MazeGenerator.md).
- Code reviews and suggestions for the PERFECT flag implementation.

All AI-generated code was reviewed, tested, and understood before integration.

## Team and project management

### Roles
- **Rirandri**: MLX graphical renderer, configuration parsing, output file format
- **Rirazafi**: ASCII terminal renderer, maze generator, fix rendering bugs, user interface

### Planning

| Phase | Tasks | Status |
|-------|-------|--------|
| 1 | Maze generator (DFS + BFS) | Done |
| 2 | Configuration parsing + output | Done |
| 3 | ASCII renderer + interactive menu | Done |
| 4 | MLX renderer + keyboard controls | Done |
| 5 | Bug fixes (terminal scroll, duplicate lines) | Done |
| 6 | PERFECT flag + entry/exit validation | Done |
| 7 | Documentation (README, MD files) | Done |
| 8 | Build system (pyproject.toml, package) | Done |

### What worked well
- The recursive backtracker algorithm was straightforward to implement and produces visually pleasing mazes.
- Using a bitmask for walls made the code clean and efficient.
- Separating the maze generator into a standalone module ensured clean architecture.

### What could be improved
- Add animation during maze generation (visual feedback of the carving process).
- Support multiple generation algorithms (Kruskal, Prim).
- Add unit tests with pytest.
- Improve MLX rendering performance with larger mazes.

### Tools used
- Python 3.13, flake8, mypy, build
- MiniLibX (42 graphical library)
- Vim / VS Code for development
- Git for version control
