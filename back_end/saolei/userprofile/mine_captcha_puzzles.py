"""
Mine-sweeper captcha puzzle bank.

Each puzzle:
- top: 5 integers shown on the top row (numbers indicate count of adjacent
  mines using standard minesweeper 8-direction adjacency).
- mines: 0-based indices of cells in the bottom row that are mines.

The expected captcha answer is the complement set (non-mine indices); the
user must click open every non-mine cell to pass.

All three initial puzzles have a unique solution under the 8-direction rule.
"""

PUZZLES: list[tuple[list[int], list[int]]] = [
    ([1, 2, 1, 2, 1], [0, 2, 4]),   # M _ M _ M     safe = {1, 3}
    ([1, 2, 3, 2, 1], [1, 2, 3]),   # _ M M M _     safe = {0, 4}
    ([1, 1, 2, 1, 1], [1, 3]),      # _ M _ M _     safe = {0, 2, 4}
]
