"""Simulations built from a game's payoff matrix, so they always agree with the solver.

You choose a row. The other player then picks a column with the probabilities of an equilibrium mix.
Your payoff decides the ending: victory if it reaches the equilibrium value for you, failure if it falls short.
"""

from fractions import Fraction

from .solver import support_equilibria


DESCRIPTIONS = {
    "equilibrium": "the equilibrium mix",
    "uniform": "a uniform random mix, not equilibrium play",
    "noisy": "a noisy best response: the better their payoff, the more likely they choose it (lambda {lam:g})",
    "loss-averse": "a loss-averse response: they weigh falling below their average payoff about 2.25 times as heavily as gaining above it (lambda {lam:g})",
}


def loss_averse_response(matrix, row, lam):
    """Logit choice with loss aversion: payoffs below the row average count 2.25 times as much."""
    import math

    payoffs = [float(matrix[row][j][1]) for j in range(len(matrix[row]))]
    reference = sum(payoffs) / len(payoffs)
    utilities = [x if x >= reference else reference + LOSS_AVERSION * (x - reference) for x in payoffs]
    top = max(utilities)
    weights = [math.exp(lam * (u - top)) for u in utilities]
    total = sum(weights)
    return [w / total for w in weights]


def noisy_response(matrix, row, lam):
    """Logit choice: the column player picks each column with weight exp(lam * payoff), given your row."""
    import math

    payoffs = [float(matrix[row][j][1]) for j in range(len(matrix[row]))]
    top = max(payoffs)
    weights = [math.exp(lam * (x - top)) for x in payoffs]
    total = sum(weights)
    return [w / total for w in weights]


OPPONENTS = ("equilibrium", "uniform", "noisy", "loss-averse")

LOSS_AVERSION = 2.25  # prospect theory: losses weigh about 2.25 times as much as gains


def matrix_simulation(game, families, opponent="equilibrium", lam=2.0):
    """opponent='equilibrium' plays the equilibrium mix; 'uniform' picks every column equally often.

    The victory line is the equilibrium value either way, so the uniform opponent shows how a plan
    fares when the other side is not playing equilibrium.
    """
    if opponent not in OPPONENTS:
        raise ValueError(f"opponent must be one of {', '.join(OPPONENTS)}")
    matrix_spec = game.get("matrix")
    if not matrix_spec:
        raise ValueError(f"'{game['name']}' has no payoff matrix")
    rows, cols = matrix_spec["rows"], matrix_spec["cols"]
    matrix = [[(Fraction(a), Fraction(b)) for a, b in row] for row in matrix_spec["payoffs"]]
    equilibria = support_equilibria(matrix)
    if not equilibria:
        raise ValueError(f"'{game['name']}' has no equilibrium to build a simulation from")
    row_mix, col_mix = equilibria[0]
    value = sum(row_mix[i] * col_mix[j] * matrix[i][j][0] for i in range(len(rows)) for j in range(len(cols)))
    if opponent == "uniform":
        col_mix = [Fraction(1, len(cols))] * len(cols)
    if opponent == "noisy" and lam < 0:
        raise ValueError("lambda must be zero or more")

    nodes = {}
    start_options = []
    for i, row_name in enumerate(rows):
        branches = []
        if opponent == "noisy":
            probs = noisy_response(matrix, i, lam)
        elif opponent == "loss-averse":
            probs = loss_averse_response(matrix, i, lam)
        else:
            probs = [float(p) for p in col_mix]
        for j, col_name in enumerate(cols):
            if probs[j] == 0:
                continue
            a, b = matrix[i][j]
            # Against an equilibrium mix nothing can beat the equilibrium value, so the test is whether you reach it.
            if a >= value:
                outcome, text = "victory", f"You get {a} against their {b}: at least the equilibrium value {float(value):g}."
            else:
                outcome, text = "failure", f"You get {a} against their {b}: below the equilibrium value {float(value):g}."
            end_id = f"end-{i}-{j}"
            nodes[end_id] = {"type": "end", "outcome": outcome, "text": text}
            branches.append({"p": probs[j], "label": f"They play {col_name}", "next": end_id,
                             "why": f"They play {col_name} {probs[j]:.0%} of the time against {rows[i]}. Your payoff: {a}."})
        nature_id = f"chance-{i}"
        nodes[nature_id] = {"type": "nature", "prompt": f"After you play {row_name}, they choose:", "branches": branches}
        start_options.append({"label": f"Play {row_name}", "next": nature_id,
                              "why": f"Playing {row_name} faces their equilibrium mix; the outcome depends on what they choose."})
    nodes["n0"] = {"type": "player", "prompt": "Choose your action.", "options": start_options}
    return {
        "id": f"{game['id']}-matrix",
        "name": f"{game['name']} (from its payoff matrix)",
        "families": families,
        "summary": f"Built from the payoff grid of {game['name']}. The equilibrium value for you is {float(value):g}. The other player's choices follow {DESCRIPTIONS[opponent].format(lam=lam)}.",
        "start": "n0",
        "nodes": nodes,
    }
