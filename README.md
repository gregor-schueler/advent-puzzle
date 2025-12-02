<div align="center">
  <a href="https://advent-puzzle.streamlit.app/">
    <img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" alt="Streamlit App" width="250">
  </a>
</div>

## Advent Puzzle Solver

Brute-force solver and terminal visualizer for a custom 4×6 Advent calendar puzzle. The board has 24 cells (4 columns × 6 rows). You remove exactly one target cell (representing a given day), then tile the remaining 23 cells with six one-sided polyomino pieces:

- `A`: length-4 bar
- `B`: length-3 bar
- `C`: 2×2 square
- `D`: skewed Z shape (two vertical dominoes offset by one)
- `E`: L shape of height 3 with a foot on the bottom-right
- `F`: T-like column with a right arm in the middle

Each piece is available **once**, but can be rotated in 90° increments (no flips).

## How the Solver Works

`solver.py` turns the tiling task into a constrained search:

1. **Define canonical rotations** – For every piece we build all unique right-angle rotations by normalizing each rotated shape to an origin-based coordinate system.
2. **Enumerate placements** – We slide every rotated piece across the 4×6 grid, producing placements that stay within bounds and do not cover the target cell. Each placement records the piece name and the four or three covered cell indices.
3. **Exact-cover search** – A recursive backtracking function chooses the uncovered cell with the fewest legal placements (most-constrained heuristic). It tries each placement whose piece is still unused and whose cells are currently free, marking cells/piece usage before recursing. When all non-target cells are filled and each piece was used exactly once, we record the placement list as a valid solution.
4. **Visualization** – Every solution is printed as a colored grid using ANSI escape codes. Occupied cells show a colored `■` (ASCII 254) tied to their piece letter, while the removed day renders as `X`.

The solver explores the complete search tree, so it prints every tiling for the selected target position. With only six pieces, exhaustive search finishes in well under a second.

## Main Objects & Functions

`solver.py` is intentionally small; these are the important pieces:

| Function / Object | Purpose |
| --- | --- |
| `PIECE_BASES` | Dict of piece names to their canonical cell offsets (before rotation). |
| `PIECE_COUNTS` | Keeps track of how many times each piece may be used (all set to 1). |
| `build_piece_rotations()` | Generates the deduplicated 90° rotations for each piece. |
| `parse_target(argv)` | Converts CLI input like `2 4` or `2,4` into the zero-based cell index to leave empty. |
| `generate_placements(target_idx, pieces)` | Lists every board placement per rotation and maps cells to the placement IDs covering them. |
| `choose_cell(...)` | Chooses the uncovered cell with the smallest number of viable placements to reduce branching. |
| `search(...)` | Backtracking engine that marks cells, decrements `pieces_left`, and appends full tilings to `solutions`. |
| `solve(target_idx)` | Orchestrates piece generation, placement enumeration, and kicks off the recursive search; returns all solutions plus the placement catalog. |
| `render_solutions(...)` | Prints the number of solutions and renders each board using colored `■` blocks plus an `X` for the missing day. |
| `main()` | Parses CLI arguments, runs `solve`, and displays the solutions.


## Running the Solver

run from the terminal with Python 3:

```bash
python solver.py 2 4
# or
python solver.py 2,4
```

Both commands leave the cell at column 2, row 4 (1-based) empty and print every tiling that respects the one-piece-each constraint. Adjust the numbers for any of the 24 possible target days.

Each run ends with a legend reminding you that colored `■` symbols mark pieces and `X` marks the missing day.
