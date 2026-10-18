"""Repeated play: a payoff matrix played for 1 to 50 rounds against a bot that remembers the game.

Each bot answers from the history so far, so a player who notices the pattern can exploit it:

  tit-for-tat  copies your previous row (the first move is the first column)
  grim         plays the first column until you ever leave the first row, then the last column for good
  pattern      cycles through the columns in order, one per round
  learner      tracks which row you pick most often and answers with its best reply to it
  wsls         win-stay, lose-shift: keeps its last column while it does well, switches when it does badly
  random       picks a column at random (a fixed seed, so a run can be repeated exactly)

The random generator is a simple linear congruential one, written the same way in the Go version,
so the same seed gives the same game in both. Every rule is deterministic apart from random.
"""

OPPONENTS = ("tit-for-tat", "grim", "pattern", "learner", "wsls", "random")
MAX_ROUNDS = 50

DESCRIPTIONS = {
    "tit-for-tat": "The bot copies your previous move. Exploiting it for one round costs you the next.",
    "grim": "The bot cooperates (plays its first column) until you leave your first row once, then defects for good.",
    "pattern": "The bot cycles through its options in a fixed order. The cycle is learnable from memory.",
    "learner": "The bot tracks which row you pick most often and answers with its best reply to it. A fixed habit is punished; varying your choices keeps it guessing.",
    "wsls": "The bot keeps its last choice while it does well and switches when it does badly. Find the moves that keep it satisfied.",
    "random": "The bot picks at random. No pattern to learn, so the best plan is the one with the highest average.",
}


class Lcg:
    """A small deterministic random generator, so the same seed gives the same run in both versions."""

    def __init__(self, seed):
        self.state = seed & 0x7FFFFFFF

    def next_below(self, n):
        self.state = (self.state * 1103515245 + 12345) & 0x7FFFFFFF
        return self.state % n


def _their_payoff(matrix, row, col):
    return matrix["payoffs"][row][col][1]


def _best_reply(matrix, row):
    """The column that pays the bot most when you play `row`. Ties go to the lowest column."""
    cols = range(len(matrix["cols"]))
    return max(cols, key=lambda c: (_their_payoff(matrix, row, c), -c))


def opponent_column(name, matrix, history, rng):
    """The column the bot plays this round, from the history of (your row, its column) so far."""
    cols = len(matrix["cols"])
    if name == "tit-for-tat":
        return history[-1][0] % cols if history else 0
    if name == "grim":
        defected = any(row != 0 for row, _ in history)
        return cols - 1 if defected else 0
    if name == "pattern":
        return len(history) % cols
    if name == "learner":
        if not history:
            return 0
        counts = [0] * len(matrix["rows"])
        for row, _ in history:
            counts[row] += 1
        favourite = max(range(len(counts)), key=lambda r: (counts[r], -r))
        return _best_reply(matrix, favourite)
    if name == "wsls":
        if not history:
            return 0
        last_row, last_col = history[-1]
        cells = [_their_payoff(matrix, r, c) for r in range(len(matrix["rows"])) for c in range(cols)]
        aspiration = sum(cells) // len(cells)
        if _their_payoff(matrix, last_row, last_col) >= aspiration:
            return last_col
        return (last_col + 1) % cols
    if name == "random":
        return rng.next_below(cols)
    raise ValueError(f"unknown opponent '{name}'")


def play_repeated(matrix, rounds, opponent, ask, say, seed=1):
    """Play the matrix for `rounds` rounds. ask(round_number, history) returns your row index.
    Returns (history, total) where history is a list of (your_row, their_col, your_payoff, their_payoff)."""
    rng = Lcg(seed)
    history = []
    for number in range(1, rounds + 1):
        row = ask(number, history)
        col = opponent_column(opponent, matrix, [(r, c) for r, c, _, _ in history], rng)
        mine, theirs = matrix["payoffs"][row][col]
        history.append((row, col, mine, theirs))
        say(number, row, col, mine, theirs)
    return history, sum(mine for _, _, mine, _ in history)


def best_fixed_plan(matrix, rounds, opponent, seed=1):
    """The best total from always playing the same row against this bot: a reference for how well you did."""
    best = None
    for row in range(len(matrix["rows"])):
        rng = Lcg(seed)
        history = []
        for _ in range(rounds):
            col = opponent_column(opponent, matrix, [(r, c) for r, c, _, _ in history], rng)
            mine, theirs = matrix["payoffs"][row][col]
            history.append((row, col, mine, theirs))
        total = sum(mine for _, _, mine, _ in history)
        if best is None or total > best[1]:
            best = (row, total)
    return best


def outcome_for_log(total, best_total):
    """How a repeated run counts in your records: a win if you matched the best fixed plan,
    a draw if you reached 80% of it, otherwise a loss."""
    if total >= best_total:
        return "win"
    if best_total > 0 and total * 5 >= best_total * 4:
        return "draw"
    return "loss"


def check_rounds(value):
    if not 1 <= value <= MAX_ROUNDS:
        raise ValueError(f"rounds must be from 1 to {MAX_ROUNDS}")
    return value
