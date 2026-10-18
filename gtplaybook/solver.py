"""Analysis of two-player games given as a payoff matrix.

Uses exact fractions. Covers iterated elimination of strictly dominated strategies,
pure-strategy Nash equilibria, maximin (security) values, and the mixed equilibrium
of 2x2 games. Mixed equilibria of larger games are not computed.
"""

from fractions import Fraction
from itertools import combinations


def parse_matrix(text):
    """Parse 'a,b c,d; e,f g,h' into rows of (your payoff, their payoff) pairs."""
    rows = [chunk.split() for chunk in text.split(";") if chunk.strip()]
    if not rows:
        raise ValueError("the payoff matrix is empty")
    matrix = []
    for cells in rows:
        row = []
        for cell in cells:
            parts = cell.split(",")
            if len(parts) != 2:
                raise ValueError(f"cell '{cell}' must look like yours,theirs, e.g. 3,5")
            row.append((Fraction(parts[0]), Fraction(parts[1])))
        matrix.append(row)
    if len({len(row) for row in matrix}) != 1:
        raise ValueError("every row needs the same number of cells")
    return matrix


def analyse(matrix):
    rows, cols = len(matrix), len(matrix[0])

    # Iterated elimination of strictly dominated strategies.
    alive_rows, alive_cols = set(range(rows)), set(range(cols))
    eliminated = []
    changed = True
    while changed:
        changed = False
        for i in sorted(alive_rows):
            if any(all(matrix[k][j][0] > matrix[i][j][0] for j in alive_cols) for k in alive_rows if k != i):
                alive_rows.discard(i)
                eliminated.append(("row", i))
                changed = True
        for j in sorted(alive_cols):
            if any(all(matrix[i][k][1] > matrix[i][j][1] for i in alive_rows) for k in alive_cols if k != j):
                alive_cols.discard(j)
                eliminated.append(("col", j))
                changed = True

    # Pure Nash equilibria: no player can gain by switching alone.
    equilibria = []
    for i in range(rows):
        for j in range(cols):
            row_best = all(matrix[i][j][0] >= matrix[k][j][0] for k in range(rows))
            col_best = all(matrix[i][j][1] >= matrix[i][l][1] for l in range(cols))
            if row_best and col_best:
                equilibria.append((i, j))

    # Maximin: the best guaranteed floor each side can secure with a pure action.
    row_floor = [min(cell[0] for cell in row) for row in matrix]
    col_floor = [min(matrix[i][j][1] for i in range(rows)) for j in range(cols)]
    row_maximin = max(row_floor)
    col_maximin = max(col_floor)

    return {
        "eliminated": eliminated,
        "surviving_rows": sorted(alive_rows),
        "surviving_cols": sorted(alive_cols),
        "equilibria": equilibria,
        "row_maximin": (row_maximin, [i for i in range(rows) if row_floor[i] == row_maximin]),
        "col_maximin": (col_maximin, [j for j in range(cols) if col_floor[j] == col_maximin]),
        "mixed": mixed_2x2(matrix) if rows == 2 and cols == 2 else None,
        "constant_sum": constant_sum(matrix),
    }


def mixed_2x2(matrix):
    """Return (p, q): row plays its first action with probability p, column with q. None if not interior."""
    (a00, b00), (a01, b01) = matrix[0]
    (a10, b10), (a11, b11) = matrix[1]
    row_den = a00 - a10 - a01 + a11
    col_den = b00 - b01 - b10 + b11
    if row_den == 0 or col_den == 0:
        return None
    p = (b11 - b10) / col_den
    q = (a11 - a01) / row_den
    if 0 < p < 1 and 0 < q < 1:
        return p, q
    return None


def constant_sum(matrix):
    totals = {a + b for row in matrix for a, b in row}
    return totals.pop() if len(totals) == 1 else None


def _solve_exact(matrix_rows, rhs):
    """Solve a square system exactly with fractions. Returns None if the system is singular."""
    n = len(rhs)
    a = [list(row) + [rhs[i]] for i, row in enumerate(matrix_rows)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if a[r][col] != 0), None)
        if pivot is None:
            return None
        a[col], a[pivot] = a[pivot], a[col]
        for r in range(n):
            if r != col and a[r][col] != 0:
                factor = a[r][col] / a[col][col]
                a[r] = [x - factor * y for x, y in zip(a[r], a[col])]
    return [a[i][n] / a[i][i] for i in range(n)]


def _indifferent_mix(payoff, own, others):
    """Mix over `own` so that every action in `others` earns the same value v. Returns (mix, v) or None.

    payoff[own_index][other_index] is the payoff to the opponent of the player who mixes over `others`.
    """
    k = len(own)
    rows, rhs = [], []
    for j in others:
        rows.append([payoff[i][j] for i in own] + [Fraction(-1)])
        rhs.append(Fraction(0))
    rows.append([Fraction(1)] * k + [Fraction(0)])
    rhs.append(Fraction(1))
    solution = _solve_exact(rows, rhs)
    if solution is None:
        return None
    return solution[:k], solution[k]


def transpose(grid):
    return [list(column) for column in zip(*grid)]


def support_equilibria(matrix):
    """All Nash equilibria in mixed or pure strategies found by support enumeration (games up to 4x4).

    Returns a list of (row_mix, col_mix) with exact fractions, where each mix is over all actions.
    """
    rows, cols = len(matrix), len(matrix[0])
    if rows > 4 or cols > 4:
        raise ValueError("support enumeration is limited to games up to 4x4")
    a = [[matrix[i][j][0] for j in range(cols)] for i in range(rows)]
    b = [[matrix[i][j][1] for j in range(cols)] for i in range(rows)]
    found = []
    for size in range(1, min(rows, cols) + 1):
        for row_support in combinations(range(rows), size):
            for col_support in combinations(range(cols), size):
                # Column player's mix q makes the row player indifferent across row_support.
                q = _indifferent_mix(transpose(a), list(col_support), list(row_support))
                # Row player's mix p makes the column player indifferent across col_support.
                p = _indifferent_mix(b, list(row_support), list(col_support))
                if q is None or p is None:
                    continue
                q_part, u = q
                p_part, v = p
                if any(x <= 0 for x in q_part) or any(x <= 0 for x in p_part):
                    continue
                row_mix = [Fraction(0)] * rows
                col_mix = [Fraction(0)] * cols
                for idx, i in enumerate(row_support):
                    row_mix[i] = p_part[idx]
                for idx, j in enumerate(col_support):
                    col_mix[j] = q_part[idx]
                # No action outside the support may earn more than the equilibrium value.
                row_values = [sum(a[i][j] * col_mix[j] for j in range(cols)) for i in range(rows)]
                col_values = [sum(b[i][j] * row_mix[i] for i in range(rows)) for j in range(cols)]
                if max(row_values) != u or max(col_values) != v:
                    continue
                if (row_mix, col_mix) not in found:
                    found.append((row_mix, col_mix))
    return found
