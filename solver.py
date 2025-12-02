#!/usr/bin/env python3
"""Brute-force tiling solver for the 4x6 Advent puzzle."""
from __future__ import annotations

from typing import Dict, List, Sequence, Set, Tuple
import sys

WIDTH = 4
HEIGHT = 6
TOTAL_CELLS = WIDTH * HEIGHT
BLOCK = "\u25A0"  # ASCII 254 / solid square
RESET = "\033[0m"
PIECE_COLORS: Dict[str, str] = {
    "A": "\033[31m", # Red
    "B": "\033[32m", # Green
    "C": "\033[33m", # Yellow
    "D": "\033[34m", # Blue
    "E": "\033[35m", # Magenta
    "F": "\033[36m", # Cyan
}

# Base piece definitions using (x, y) offsets from origin.
PIECE_BASES: Dict[str, Sequence[Tuple[int, int]]] = {
    "A": [(0, 0), (1, 0), (2, 0), (3, 0)],
    "B": [(0, 0), (1, 0), (2, 0)],
    "C": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "D": [(0, 0), (0, 1), (1, 1), (1, 2)],
    "E": [(0, 0), (0, 1), (0, 2), (1, 2)],
    "F": [(0, 0), (0, 1), (0, 2), (1, 1)],
}

# Each piece is available exactly once so the covered area totals 23 cells.
PIECE_COUNTS: Dict[str, int] = {name: 1 for name in PIECE_BASES}


def rotate(shape: Sequence[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Rotate shape 90 degrees clockwise around the origin."""
    return [(-y, x) for x, y in shape]


def normalize(shape: Sequence[Tuple[int, int]]) -> Tuple[Tuple[int, int], ...]:
    """Translate shape so its minimum x/y is at the origin."""
    min_x = min(x for x, _ in shape)
    min_y = min(y for _, y in shape)
    return tuple(sorted((x - min_x, y - min_y) for x, y in shape))


def build_piece_rotations() -> Dict[str, List[List[Tuple[int, int]]]]:
    """Return all unique 90° rotations for every piece."""
    pieces: Dict[str, List[List[Tuple[int, int]]]] = {}
    for name, base in PIECE_BASES.items():
        seen: Set[Tuple[Tuple[int, int], ...]] = set()
        orientations: List[List[Tuple[int, int]]] = []
        shape = list(base)
        for _ in range(4):
            norm = normalize(shape)
            if norm not in seen:
                seen.add(norm)
                orientations.append(list(norm))
            shape = rotate(shape)
        pieces[name] = orientations
    return pieces


def parse_target(argv: Sequence[str]) -> int:
    """Parse the target coordinate (1-based x, y)."""
    if not argv:
        raise SystemExit(
            "Usage: python solver.py <x> <y>  # 1<=x<=4, 1<=y<=6 (or 'x,y')"
        )

    if len(argv) == 1 and "," in argv[0]:
        parts = argv[0].split(",")
    else:
        parts = argv[:2]
    if len(parts) < 2:
        raise SystemExit("Expected two integers for target location")

    try:
        x = int(parts[0])
        y = int(parts[1])
    except ValueError as exc:
        raise SystemExit("Target coordinates must be integers") from exc

    if not (1 <= x <= WIDTH and 1 <= y <= HEIGHT):
        raise SystemExit(
            f"Target must be within 1<=x<= {WIDTH}, 1<=y<={HEIGHT}; got ({x}, {y})"
        )
    return (y - 1) * WIDTH + (x - 1)


def generate_placements(
    target_idx: int, pieces: Dict[str, List[List[Tuple[int, int]]]]
) -> Tuple[List[Dict[str, Sequence[int]]], List[List[int]]]:
    """Enumerate every placement that avoids the target cell."""
    placements: List[Dict[str, Sequence[int]]] = []
    placements_by_cell: List[List[int]] = [list() for _ in range(TOTAL_CELLS)]

    for name, orientations in pieces.items():
        for orientation in orientations:
            width = max(x for x, _ in orientation) + 1
            height = max(y for _, y in orientation) + 1
            for oy in range(HEIGHT - height + 1):
                for ox in range(WIDTH - width + 1):
                    cells: List[int] = []
                    for dx, dy in orientation:
                        x = ox + dx
                        y = oy + dy
                        cell = y * WIDTH + x
                        cells.append(cell)
                    if target_idx in cells:
                        continue
                    pid = len(placements)
                    placements.append({"piece": name, "cells": tuple(cells)})
                    for cell in cells:
                        placements_by_cell[cell].append(pid)
    return placements, placements_by_cell


def choose_cell(
    uncovered: Set[int],
    filled: Sequence[bool],
    placements: Sequence[Dict[str, Sequence[int]]],
    placements_by_cell: Sequence[Sequence[int]],
    pieces_left: Dict[str, int],
) -> Tuple[int, int]:
    """Select the uncovered cell with the fewest viable placements."""
    best_cell = -1
    best_options = sys.maxsize
    for cell in uncovered:
        options = 0
        for pid in placements_by_cell[cell]:
            placement = placements[pid]
            if pieces_left[placement["piece"]] == 0:
                continue
            if any(filled[c] for c in placement["cells"]):
                continue
            options += 1
        if options == 0:
            return cell, 0
        if options < best_options:
            best_options = options
            best_cell = cell
            if best_options == 1:
                break
    return best_cell, best_options


def search(
    uncovered: Set[int],
    filled: List[bool],
    placements: Sequence[Dict[str, Sequence[int]]],
    placements_by_cell: Sequence[Sequence[int]],
    solution: List[int],
    pieces_left: Dict[str, int],
    solutions: List[Tuple[int, ...]],
) -> None:
    if not uncovered:
        if all(count == 0 for count in pieces_left.values()):
            solutions.append(tuple(solution))
        return

    cell, options = choose_cell(
        uncovered, filled, placements, placements_by_cell, pieces_left
    )
    if options == 0:
        return

    for pid in placements_by_cell[cell]:
        placement = placements[pid]
        piece_name = placement["piece"]
        if pieces_left[piece_name] == 0:
            continue
        placement_cells = placement["cells"]
        if any(filled[c] for c in placement_cells):
            continue
        solution.append(pid)
        pieces_left[piece_name] -= 1
        removed: List[int] = []
        for c in placement_cells:
            if not filled[c]:
                filled[c] = True
                uncovered.remove(c)
                removed.append(c)
        search(
            uncovered,
            filled,
            placements,
            placements_by_cell,
            solution,
            pieces_left,
            solutions,
        )
        for c in removed:
            filled[c] = False
            uncovered.add(c)
        solution.pop()
        pieces_left[piece_name] += 1


def solve(target_idx: int) -> Tuple[List[Dict[str, Sequence[int]]], List[Tuple[int, ...]]]:
    pieces = build_piece_rotations()
    placements, placements_by_cell = generate_placements(target_idx, pieces)
    uncovered = {cell for cell in range(TOTAL_CELLS) if cell != target_idx}
    filled = [False] * TOTAL_CELLS
    filled[target_idx] = True
    solution: List[int] = []
    pieces_left = PIECE_COUNTS.copy()
    all_solutions: List[Tuple[int, ...]] = []
    search(
        uncovered,
        filled,
        placements,
        placements_by_cell,
        solution,
        pieces_left,
        all_solutions,
    )
    if not all_solutions:
        raise RuntimeError("No tiling found for this target cell")
    return placements, all_solutions


def render_solutions(
    placements: Sequence[Dict[str, Sequence[int]]],
    solutions: Sequence[Sequence[int]],
    target_idx: int,
) -> None:
    print(f"Found {len(solutions)} solution(s).")
    for idx, solution_ids in enumerate(solutions, start=1):
        print(f"\nSolution {idx}:")
        grid: List[str] = [" "] * TOTAL_CELLS
        for pid in solution_ids:
            placement = placements[pid]
            color = PIECE_COLORS[placement["piece"]]
            for cell in placement["cells"]:
                grid[cell] = f"{color}{BLOCK}{RESET}"
        grid[target_idx] = "X"

        for y in range(HEIGHT):
            row = grid[y * WIDTH : (y + 1) * WIDTH]
            print(" ".join(row))
    print()
    print("Legend: \u25A0 in fixed colors per piece, 'X' marks the target day.")


def main() -> None:
    target_idx = parse_target(sys.argv[1:])
    placements, solutions = solve(target_idx)
    render_solutions(placements, solutions, target_idx)


if __name__ == "__main__":
    main()
