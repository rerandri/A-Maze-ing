*This project has been created as part of the 42 curriculum by <login1>[, <login2>[, <login3>[...]]].*

# A-Maze-ing

## Description

**A-Maze-ing** is a maze generation project developed in Python as part of the 42 curriculum.  
The main goal is to design and implement a system capable of generating valid mazes while applying clean software architecture, algorithmic reasoning, and team collaboration practices.

At a high level, the project:
- Builds a maze data structure from a configurable setup.
- Generates the maze using a selected generation algorithm.
- Optionally supports visualization or export depending on implementation choices.
- Emphasizes reusable components for future maze-based projects (solvers, games, pathfinding demos, etc.).

---

## Features

- Maze generation with a deterministic or random strategy.
- Config-driven setup (size, seed, optional display/output options).
- Modular Python codebase with reusable logic.
- Team-oriented development workflow.

If advanced features are implemented, include them here:
- Multiple maze generation algorithms (`Recursive Backtracking`, `Prim`, `Kruskal`, etc.).
- Different display modes (ASCII, graphical, step-by-step).
- Configurable randomness seed for reproducibility.
- Export to file / load from file.

---

## Instructions

### Prerequisites

- Python 3.10+ (or your actual version)
- `pip` (Python package manager)

### Installation

```bash
git clone git@vogsphere.42antananarivo.mg:vogsphere/intra-uuid-c42b910e-c46c-4398-9f62-2080a43720ec-7346472-rerandri A-Maze-ing 
cd A-Maze-ing
python3 -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate
make install
```

### Compilation

No compilation is required for pure Python projects.  
(If your project includes C extensions or build steps, document them here.)

### Execution

```bash
make run
```

Or

```bash
python3 a_maze_ing.py config.txt
```

### Usage Examples

```bash
#configure parametre in file 'config.txt'
Generating maze with dimensions 30x30 ...
Maze generated and saved to 'maze.txt'

=== A-Maze-ing ===
 [1].Re-generate maze
 [2].Display maze
 [3].Show path: [OFF]
 [4].Reveal animation: [ON]
 [5].Rotate maze colors
 [6].Cycle '42' pattern colors
 [7].Quit

Type /help for more commands.
Maze>> 2
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
Info for maze:
Entry : ██ | Exit : ██ | Path : ██ | wall : ██ | '42' pattern : ██

Size : 30 x 30
Animation delay : 0.03s
Reveal animation : ON
Show path : OFF

```

---

## Config File Structure

> Replace this with your **real and complete** config format.

Example (`config.txt`):

```txt
# ---- SIZE ----
WIDTH=30
HEIGHT=30

# ---- START ----
ENTRY=29,1
EXIT=1,29

# ---- OUTPUT FILE ----
OUTPUT_FILE=maze.txt

# ---- OPTIONAL ----
PERFECT=true
SEED=42
```

### Field Reference

- `maze.width` *(int)*: Number of columns.
- `maze.height` *(int)*: Number of rows.
- `maze.algorithm` *(string)*: Selected generation algorithm.
- `maze.seed` *(int | null)*: Random seed for reproducibility.
- `display.mode` *(string)*: Display backend (`ascii`, `gui`, etc.).
- `display.show_generation_steps` *(bool)*: Step-by-step rendering.
- `output.save_to_file` *(bool)*: Enables export.
- `output.file_path` *(string)*: Export destination.

---

## Maze Generation Algorithm

### Chosen Algorithm: Recursive Backtracking (Depth-First Search)

The maze is generated by:
1. Starting from an initial cell.
2. Randomly visiting an unvisited neighbor.
3. Removing the wall between current and next cell.
4. Recursively continuing until dead-end.
5. Backtracking to the latest cell with unvisited neighbors.

### Why this algorithm

We chose Recursive Backtracking because it:
- Is simple and robust to implement.
- Produces “natural-looking” mazes with long corridors.
- Performs efficiently for typical project sizes.
- Is easy to explain, debug, and extend in a pedagogical context.

(If you used another algorithm, replace this section accordingly.)

---

## Reusable Parts of the Code

The following components are designed for reuse:

- **Grid/Cell model**: Can be reused in any grid-based generation/solver project.
- **Neighbor and wall utilities**: Shared by different algorithms.
- **Algorithm interface**: Allows plugging in additional generation strategies.
- **Config loader/validator**: Reusable in future Python CLI projects.
- **Renderer/exporter**: Can support multiple output formats without changing core logic.

How to reuse:
- Import the core maze package/module into another project.
- Implement the same algorithm interface for new generators.
- Reuse renderer independently for visualization tasks.

---

## Team & Project Management

### Team Roles

- **<login1>** — Project coordination, core architecture, algorithm integration.
- **<team_member_2>** — Data structures, config parsing, tests.
- **<team_member_3>** — Rendering/output, documentation, tooling.

(Adjust to your real team and contributions.)

### Planning: Initial vs Final

**Initial plan**
- Week 1: architecture + base data model
- Week 2: algorithm implementation + validation
- Week 3: rendering/output + polishing + README

**How it evolved**
- Added extra time for debugging edge cases (small grids, invalid config).
- Refactored modules for better reuse.
- Documentation expanded to support onboarding for non-technical readers.

### What Worked Well

- Clear task split per module.
- Frequent sync points reduced merge conflicts.
- Early testing on edge cases improved stability.

### What Could Be Improved

- Define coding conventions earlier.
- Add CI checks sooner (lint/tests on every push).
- Allocate more time for benchmark/comparison across algorithms.

### Tools Used

- **GitHub** (version control, PR review, issue tracking)
- **Python virtual environment + pip**
- **Linters/formatters** (e.g., `ruff`, `flake8`, `black`) *(if used)*
- **Project board / task tracker** (GitHub Projects, Notion, Trello, etc.) *(if used)*

---

## Resources

### Maze & Algorithm References

- Jamis Buck — *Mazes for Programmers*
- Wikipedia — Maze generation algorithm overview
- Red Blob Games — Grid/graph/pathfinding references
- Python official documentation

### Practical Tutorials / Documentation

- Python docs: https://docs.python.org/3/
- Network/graph concepts (if applicable): https://networkx.org/documentation/
- CLI parsing (if using argparse): https://docs.python.org/3/library/argparse.html

### AI Usage Disclosure

AI tools were used to support:
- README structure and writing clarity.
- Refactoring suggestions for readability.
- Drafting test-case ideas and edge-case checklists.
- Explaining and comparing generation algorithms during design discussions.

AI was **not** used as a blind code replacement; all produced content was reviewed, adapted, and validated by the team.

---

## Where to Find More Information

- Repository: https://github.com/rerandri/A-Maze-ing
- Source code modules: `<src/...>` (update with real paths)
- Config examples: `<config/...>` (update with real paths)
- Team notes/project board: `<link if available>`
