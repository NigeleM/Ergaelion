"""Engine games: a computer opponent that chooses its move as you play.

Board games use a search. Tic-tac-toe and Nim are solved exactly, and Connect Four uses
alpha-beta search to a fixed depth. The matrix and military games use your history: the
engine answers the choice you have made most often, so a repeated pattern gets punished.

The Go version in goplaybook/engine.go follows the same rules, move order and tie-breaks,
so both versions play the same game.
"""

import json
from functools import lru_cache

from .catalog import DATA_DIR

C4_ROWS, C4_COLS = 6, 7
C4_ORDER = (3, 2, 4, 1, 5, 0, 6)  # centre first; ties go to the first column in this order
C4_DEPTH = 4
C4_WINDOWS = []
for _r in range(C4_ROWS):
    for _c in range(C4_COLS):
        for _dr, _dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
            _cells = [(_r + k * _dr, _c + k * _dc) for k in range(4)]
            if all(0 <= y < C4_ROWS and 0 <= x < C4_COLS for y, x in _cells):
                C4_WINDOWS.append(_cells)

WIN_LINES = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))
MOVES = ("rock", "paper", "scissors")
BEATS = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
COUNTER = {"rock": "paper", "paper": "scissors", "scissors": "rock"}
ROCK_PAPER_SCISSORS_ROUNDS = 20
BLOTTO_ROUNDS = 5
BLOTTO_UNITS = 6
BLOTTO_FRONTS = 3
PATROL_GATES = 3
PATROL_ROUNDS = 12
SEARCH_LIMIT = 1 << 30
ULTIMATUM_COINS = 10
ULTIMATUM_THRESHOLD = 3  # the engine accepts an offer of at least this many coins
ULTIMATUM_ROUNDS = 5
BEAUTY_TOP = 100  # guesses run from 0 to this
BEAUTY_OPENING = 50  # the engine's forecast of your guess before you have guessed
BEAUTY_ROUNDS = 5
PENNY_ROUNDS = 20


def engine_games():
    """The engine games, from the data file."""
    return json.loads((DATA_DIR / "engine-games.json").read_text(encoding="utf-8"))


def find_engine_game(games, query):
    key = query.strip().lower()
    for game in games:
        if game["id"] == key:
            return game
    raise ValueError(f"no engine game '{query}'. Run 'engine' to list them.")


# ---- Tic-tac-toe: X is you, O is the engine. Boards are 9-character strings, row by row.

def ttt_winner(board):
    for a, b, c in WIN_LINES:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]
    return None


@lru_cache(maxsize=None)
def ttt_value(board):
    """Score for X: 10 minus the moves made when X wins, the reverse for O, 0 for a draw."""
    filled = sum(1 for cell in board if cell != " ")
    won = ttt_winner(board)
    if won == "X":
        return 10 - filled
    if won == "O":
        return filled - 10
    if filled == 9:
        return 0
    mover = "X" if filled % 2 == 0 else "O"
    values = [ttt_value(board[:i] + mover + board[i + 1:]) for i, cell in enumerate(board) if cell == " "]
    return max(values) if mover == "X" else min(values)


def ttt_best(board, mover):
    """The best square for the player who is mover; the lowest number wins a tie."""
    best, best_value = None, None
    for i, cell in enumerate(board):
        if cell != " ":
            continue
        value = ttt_value(board[:i] + mover + board[i + 1:])
        better = best is None or (value > best_value if mover == "X" else value < best_value)
        if better:
            best, best_value = i, value
    return best


# ---- Nim: three piles, take any number from one pile, whoever takes the last object wins.

@lru_cache(maxsize=None)
def nim_wins(piles):
    """True when the player to move can force a win."""
    if not any(piles):
        return False
    for i, size in enumerate(piles):
        for take in range(1, size + 1):
            if not nim_wins(piles[:i] + (size - take,) + piles[i + 1:]):
                return True
    return False


def nim_options(piles):
    return [(i, take) for i, size in enumerate(piles) for take in range(1, size + 1)]


def nim_best(piles):
    """A winning (pile, take) when one exists, else the first legal one."""
    options = nim_options(piles)
    for i, take in options:
        if not nim_wins(piles[:i] + (piles[i] - take,) + piles[i + 1:]):
            return i, take
    return options[0]


# ---- Connect Four: X is you (first), O is the engine. grid[row][col], row 0 is the bottom.

def c4_empty():
    return [[" "] * C4_COLS for _ in range(C4_ROWS)]


def c4_winner(grid):
    for cells in C4_WINDOWS:
        first = grid[cells[0][0]][cells[0][1]]
        if first != " " and all(grid[y][x] == first for y, x in cells):
            return first
    return None


def c4_full(grid):
    return all(grid[C4_ROWS - 1][c] != " " for c in range(C4_COLS))


def c4_drop(grid, col, piece):
    for row in range(C4_ROWS):
        if grid[row][col] == " ":
            grid[row][col] = piece
            return row
    return None


def c4_score(grid):
    """Score for O: threes and twos in an open line, and the centre column."""
    total = 0
    for cells in C4_WINDOWS:
        values = [grid[y][x] for y, x in cells]
        o, x = values.count("O"), values.count("X")
        if o and x:
            continue
        if o == 3:
            total += 5
        elif o == 2:
            total += 2
        if x == 3:
            total -= 5
        elif x == 2:
            total -= 2
    for row in range(C4_ROWS):
        if grid[row][C4_COLS // 2] == "O":
            total += 3
        elif grid[row][C4_COLS // 2] == "X":
            total -= 3
    return total


def c4_search(grid, depth, alpha, beta, engine_turn):
    won = c4_winner(grid)
    if won == "O":
        return 1000 + depth
    if won == "X":
        return -1000 - depth
    if depth == 0 or c4_full(grid):
        return c4_score(grid)
    best = -SEARCH_LIMIT if engine_turn else SEARCH_LIMIT
    for col in C4_ORDER:
        row = c4_drop(grid, col, "O" if engine_turn else "X")
        if row is None:
            continue
        value = c4_search(grid, depth - 1, alpha, beta, not engine_turn)
        grid[row][col] = " "
        if engine_turn:
            best = max(best, value)
            alpha = max(alpha, best)
        else:
            best = min(best, value)
            beta = min(beta, best)
        if alpha >= beta:
            break
    return best


def c4_best(grid, engine_turn):
    """The best column for the side to move; the first column in C4_ORDER wins a tie."""
    best_col, best_value = None, None
    for col in C4_ORDER:
        row = c4_drop(grid, col, "O" if engine_turn else "X")
        if row is None:
            continue
        value = c4_search(grid, C4_DEPTH - 1, -SEARCH_LIMIT, SEARCH_LIMIT, not engine_turn)
        grid[row][col] = " "
        better = best_col is None or (value > best_value if engine_turn else value < best_value)
        if better:
            best_col, best_value = col, value
    return best_col


# ---- Rock-paper-scissors against a pattern engine.

def rps_engine_move(history):
    """Beat your most common move so far; rock is the first choice when counts tie."""
    counts = {move: history.count(move) for move in MOVES}
    predicted = max(MOVES, key=lambda move: (counts[move], -MOVES.index(move)))
    return COUNTER[predicted]


# ---- Colonel Blotto: three fronts, six units, you and the engine send at once.

BLOTTO_SPLITS = [(a, b, BLOTTO_UNITS - a - b) for a in range(BLOTTO_UNITS + 1)
                 for b in range(BLOTTO_UNITS + 1 - a)]


def blotto_net(mine, theirs):
    """Fronts won minus fronts lost by mine."""
    total = 0
    for a, b in zip(mine, theirs):
        total += (a > b) - (a < b)
    return total


def blotto_engine_split(history):
    """The split with the best net result against your past splits (all splits, if none yet)."""
    past = history or BLOTTO_SPLITS
    best, best_value = None, None
    for split in BLOTTO_SPLITS:
        value = sum(blotto_net(split, theirs) for theirs in past) / len(past)
        if best is None or value > best_value:
            best, best_value = split, value
    return best


def parse_split(text):
    parts = text.replace(",", " ").split()
    if len(parts) != BLOTTO_FRONTS or not all(part.isdigit() for part in parts):
        return None
    numbers = [int(part) for part in parts]
    return tuple(numbers) if sum(numbers) == BLOTTO_UNITS else None


# ---- Border patrol: you pick a gate to slip through, the guard watches one gate.

def patrol_engine_gate(history):
    """Watch the gate you have used most often; gate 1 when counts tie or there is no history."""
    counts = [history.count(gate) for gate in range(PATROL_GATES)]
    return max(range(PATROL_GATES), key=lambda gate: (counts[gate], -gate))


# ---- Ultimatum: you offer the engine coins out of ten. It accepts an offer of at least its threshold.

def ultimatum_accepts(engine_share):
    return engine_share >= ULTIMATUM_THRESHOLD


# ---- Guess two thirds: the target is two thirds of the average of the two guesses, which is (you + engine) // 3.

def beauty_engine_guess(history):
    """Two thirds of your average guess so far, using whole numbers."""
    if not history:
        return 2 * BEAUTY_OPENING // 3
    return 2 * sum(history) // (3 * len(history))


def beauty_target(you, engine):
    return (you + engine) // 3


# ---- Matching pennies: the engine's coin differs from the call you have made most often.

def penny_engine_coin(calls):
    """Opposite of your most common call. Heads counts as your call when the calls are tied."""
    predicted = "h" if calls.count("h") >= calls.count("t") else "t"
    return "t" if predicted == "h" else "h"


# ---- The game loop. ask(prompt) returns a line, or None at the end of input. say(text) prints.

def play(game, ask, say, catalog=None):
    """Play one engine game. Returns when the game ends or you quit. Duel games need the catalogue."""
    say("\n" + game["name"])
    say(game["rules"])
    say("")
    if game.get("kind") == "duel":
        return _play_duel(game, catalog or [], ask, say)
    if game["id"] == "tic-tac-toe":
        return _play_tic_tac_toe(ask, say)
    if game["id"] == "nim":
        return _play_nim(ask, say)
    if game["id"] == "connect-four":
        return _play_connect_four(ask, say)
    if game["id"] == "rock-paper-scissors":
        return _play_rock_paper_scissors(ask, say)
    if game["id"] == "colonel-blotto":
        return _play_blotto(ask, say)
    if game["id"] == "border-patrol":
        return _play_patrol(ask, say)
    if game["id"] == "ultimatum":
        return _play_ultimatum(ask, say)
    if game["id"] == "beauty-contest":
        return _play_beauty_contest(ask, say)
    if game["id"] == "matching-pennies":
        return _play_matching_pennies(ask, say)
    raise ValueError(f"no engine for '{game['id']}'")


def _read(ask, prompt):
    """A line from the player, or None when they quit or input ends."""
    line = ask(prompt)
    if line is None:
        return None
    line = line.strip().lower()
    return None if line in ("q", "quit", "exit") else line


def _show_board(say, board):
    """The board, with each empty square shown by its number."""
    rows = [" | ".join(board[i] if board[i] != " " else str(i + 1) for i in range(r * 3, r * 3 + 3))
            for r in range(3)]
    say("\n" + ("\n-----------\n".join(rows)) + "\n")


def _play_tic_tac_toe(ask, say):
    board = " " * 9
    say("h for a hint, q to quit.")
    _show_board(say, board)
    while True:
        line = _read(ask, "Your square (1-9): ")
        if line is None:
            say("You left the game.")
            return
        if line == "h":
            say(f"Hint: square {ttt_best(board, 'X') + 1} is the best move for you.")
            continue
        if not (line.isdigit() and 1 <= int(line) <= 9 and board[int(line) - 1] == " "):
            say("Pick an empty square from 1 to 9.")
            continue
        board = board[:int(line) - 1] + "X" + board[int(line):]
        if ttt_winner(board) or " " not in board:
            break
        engine = ttt_best(board, "O")
        board = board[:engine] + "O" + board[engine + 1:]
        say(f"Engine plays square {engine + 1}.")
        _show_board(say, board)
        if ttt_winner(board) or " " not in board:
            break
    _show_board(say, board)
    winner = ttt_winner(board)
    say("You win." if winner == "X" else "The engine wins." if winner == "O" else "A draw.")


def _play_nim(ask, say):
    piles = (3, 5, 7)
    say("h for a hint, q to quit.")
    while True:
        say("Piles: " + "  ".join(f"{i + 1}: {'o' * size or '(empty)'}" for i, size in enumerate(piles)))
        if not any(piles):
            say("You took the last object. You win.")
            return
        line = _read(ask, "Pile and count, e.g. 2 3 (or h, q): ")
        if line is None:
            say("You left the game.")
            return
        if line == "h":
            if nim_wins(piles):
                pile, take = nim_best(piles)
                say(f"Hint: take {take} from pile {pile + 1}. That keeps you winning.")
            else:
                say("Hint: against perfect play every move loses from here.")
            continue
        parts = line.replace(",", " ").split()
        if len(parts) != 2 or not all(part.isdigit() for part in parts):
            say("Enter a pile and a count, for example 2 3.")
            continue
        pile, take = int(parts[0]) - 1, int(parts[1])
        if not (0 <= pile < len(piles) and 1 <= take <= piles[pile]):
            say("That move is not allowed. Take from a pile that has objects in it.")
            continue
        piles = piles[:pile] + (piles[pile] - take,) + piles[pile + 1:]
        if not any(piles):
            say("You took the last object. You win.")
            return
        pile, take = nim_best(piles)
        piles = piles[:pile] + (piles[pile] - take,) + piles[pile + 1:]
        say(f"Engine takes {take} from pile {pile + 1}.")
        if not any(piles):
            say("The engine took the last object. The engine wins.")
            return


def _show_grid(say, grid):
    say("  " + " ".join(str(c + 1) for c in range(C4_COLS)))
    for row in reversed(range(C4_ROWS)):
        say("  " + " ".join(grid[row][c] for c in range(C4_COLS)))
    say("")


def _play_connect_four(ask, say):
    grid = c4_empty()
    say("Enter a column from 1 to 7, h for a hint, or q to quit.")
    _show_grid(say, grid)
    while True:
        line = _read(ask, "Your column (1-7): ")
        if line is None:
            say("You left the game.")
            return
        if line == "h":
            say(f"Hint: column {c4_best(grid, False) + 1} is the best move for you.")
            continue
        if not (line.isdigit() and 1 <= int(line) <= C4_COLS) or grid[C4_ROWS - 1][int(line) - 1] != " ":
            say("Pick a column from 1 to 7 that is not full.")
            continue
        c4_drop(grid, int(line) - 1, "X")
        if c4_winner(grid) or c4_full(grid):
            break
        col = c4_best(grid, True)
        c4_drop(grid, col, "O")
        say(f"Engine plays column {col + 1}.")
        _show_grid(say, grid)
        if c4_winner(grid) or c4_full(grid):
            break
    _show_grid(say, grid)
    winner = c4_winner(grid)
    say("You win." if winner == "X" else "The engine wins." if winner == "O" else "A draw.")


def _play_rock_paper_scissors(ask, say):
    names = {"r": "rock", "rock": "rock", "p": "paper", "paper": "paper", "s": "scissors", "scissors": "scissors"}
    history, you, engine = [], 0, 0
    say("Enter r, p or s. h for a hint, q quits.")
    round_number = 1
    while round_number <= ROCK_PAPER_SCISSORS_ROUNDS:
        line = _read(ask, f"Round {round_number} (r, p or s): ")
        if line is None:
            say("You left the game.")
            return
        if line == "h":
            reply = rps_engine_move(history)
            say(f"Hint: the engine will play {reply}. Play {COUNTER[reply]} to beat it.")
            continue
        if line not in names:
            say("Enter r, p or s.")
            continue
        move = names[line]
        reply = rps_engine_move(history)
        history.append(move)
        if BEATS[move] == reply:
            you += 1
            result = "You win the round."
        elif BEATS[reply] == move:
            engine += 1
            result = "The engine wins the round."
        else:
            result = "Round drawn."
        say(f"You played {move}, the engine played {reply}. {result}")
        round_number += 1
    say(f"Final score: you {you}, the engine {engine}, drawn {ROCK_PAPER_SCISSORS_ROUNDS - you - engine}.")
    say("You win the match." if you > engine else "The engine wins the match." if engine > you else "The match is drawn.")


def _play_blotto(ask, say):
    history, net_total = [], 0
    say(f"Send {BLOTTO_UNITS} units across {BLOTTO_FRONTS} fronts, for example 2 2 2. h for a hint, q quits.")
    for round_number in range(1, BLOTTO_ROUNDS + 1):
        while True:
            line = _read(ask, f"Round {round_number} split: ")
            if line is None:
                say("You left the game.")
                return
            if line == "h":
                engine_split = blotto_engine_split(history)
                best = max(BLOTTO_SPLITS, key=lambda option: blotto_net(option, engine_split))
                say(f"Hint: the engine will send {' '.join(map(str, engine_split))}. "
                    f"{' '.join(map(str, best))} does best against that.")
                continue
            split = parse_split(line)
            if split:
                break
            say(f"Enter {BLOTTO_FRONTS} whole numbers that add up to {BLOTTO_UNITS}.")
        engine = blotto_engine_split(history)
        history.append(split)
        net = blotto_net(split, engine)
        net_total += net
        say(f"You sent {' '.join(map(str, split))}, the engine sent {' '.join(map(str, engine))}.")
        say("You take the round." if net > 0 else "The engine takes the round." if net < 0 else "Round drawn.")
    say("You win the campaign." if net_total > 0 else "The engine wins the campaign." if net_total < 0
        else "The campaign is drawn.")


def _play_patrol(ask, say):
    history, through = [], 0
    say(f"Pick a gate from 1 to {PATROL_GATES}. h for a hint, q quits.")
    round_number = 1
    while round_number <= PATROL_ROUNDS:
        line = _read(ask, f"Round {round_number} gate: ")
        if line is None:
            say("You left the game.")
            return
        if line == "h":
            say("Hint: the guard watches the gate you have used most, so pick the gate you have used least.")
            continue
        if not (line.isdigit() and 1 <= int(line) <= PATROL_GATES):
            say(f"Enter a gate from 1 to {PATROL_GATES}.")
            continue
        gate = int(line) - 1
        guard = patrol_engine_gate(history)
        history.append(gate)
        if gate == guard:
            say(f"The guard was at gate {guard + 1}. You are caught.")
        else:
            through += 1
            say(f"The guard was at gate {guard + 1}. You get through.")
        round_number += 1
    say(f"You got through {through} of {PATROL_ROUNDS} times.")
    say("You win." if through > PATROL_ROUNDS // 2 else "The guard wins.")


def _play_ultimatum(ask, say):
    you_total, engine_total = 0, 0
    say(f"Enter how many of the {ULTIMATUM_COINS} coins the engine gets. h for a hint, q quits.")
    round_number = 1
    while round_number <= ULTIMATUM_ROUNDS:
        line = _read(ask, f"Round {round_number} (coins for the engine): ")
        if line is None:
            say("You left the game.")
            return
        if line == "h":
            say(f"Hint: offer the engine {ULTIMATUM_THRESHOLD} coins, the least it accepts. "
                f"You keep {ULTIMATUM_COINS - ULTIMATUM_THRESHOLD}.")
            continue
        if not (line.isdigit() and int(line) <= ULTIMATUM_COINS):
            say(f"Enter a whole number from 0 to {ULTIMATUM_COINS}.")
            continue
        share = int(line)
        if ultimatum_accepts(share):
            you_total += ULTIMATUM_COINS - share
            engine_total += share
            say(f"The engine accepts. You keep {ULTIMATUM_COINS - share} coins, it gets {share}.")
        else:
            say("The engine refuses. Neither of you gets anything this round.")
        round_number += 1
    say(f"You finished with {you_total} coins, the engine with {engine_total}.")
    say("You win." if you_total > engine_total else "The engine wins." if engine_total > you_total
        else "The match is drawn.")


def _play_beauty_contest(ask, say):
    guesses, you, engine = [], 0, 0
    say(f"Guess a whole number from 0 to {BEAUTY_TOP}. h for a hint, q quits.")
    round_number = 1
    while round_number <= BEAUTY_ROUNDS:
        line = _read(ask, f"Round {round_number} (0 to {BEAUTY_TOP}): ")
        if line is None:
            say("You left the game.")
            return
        engine_guess = beauty_engine_guess(guesses)
        if line == "h":
            say(f"Hint: the engine will guess {engine_guess}. About half of that, {engine_guess // 2}, "
                "lands closest to the target.")
            continue
        if not (line.isdigit() and int(line) <= BEAUTY_TOP):
            say(f"Enter a whole number from 0 to {BEAUTY_TOP}.")
            continue
        guess = int(line)
        guesses.append(guess)
        target = beauty_target(guess, engine_guess)
        yours, theirs = abs(guess - target), abs(engine_guess - target)
        if yours < theirs:
            you += 1
            result = "You win the round."
        elif theirs < yours:
            engine += 1
            result = "The engine wins the round."
        else:
            result = "Round drawn."
        say(f"You guessed {guess}, the engine guessed {engine_guess}. The target was {target}. {result}")
        round_number += 1
    say(f"Final score: you {you}, the engine {engine}, drawn {BEAUTY_ROUNDS - you - engine}.")
    say("You win the match." if you > engine else "The engine wins the match." if engine > you
        else "The match is drawn.")


def _play_matching_pennies(ask, say):
    calls, you, engine = [], 0, 0
    say("Call h or t. ? for a hint, q quits.")
    round_number = 1
    while round_number <= PENNY_ROUNDS:
        line = _read(ask, f"Round {round_number} (h or t): ")
        if line is None:
            say("You left the game.")
            return
        if line == "?":
            say("Hint: the engine shows the opposite of your most common call, so calling the less common one wins "
                "(tails, when tied). Mix your calls to stay unpredictable.")
            continue
        if line not in ("h", "t"):
            say("Enter h or t.")
            continue
        coin = penny_engine_coin(calls)
        calls.append(line)
        if line == coin:
            you += 1
            result = "You win the round."
        else:
            engine += 1
            result = "The engine wins the round."
        say(f"You called {line}, the engine showed {coin}. {result}")
        round_number += 1
    say(f"Final score: you {you}, the engine {engine}.")
    say("You win the match." if you > engine else "The engine wins the match." if engine > you
        else "The match is drawn.")


# ---- Duel games: a catalogue game with a payoff table. The engine answers each row with a column,
# from one of two fixed rules. The Go version in goplaybook/duel.go follows the same rules.

def duel_engine_col(matrix, played, policy):
    """The engine's column. The learner plays the column that does best against your most common row;
    the reactive engine plays the column that does best against your last row, and the first column first."""
    cols = range(len(matrix["cols"]))
    if policy == "mirror":
        if not played:
            return 0
        return played[-1] if played[-1] < len(cols) else 0
    if policy == "exploiter":
        predicted = duel_predicted_row(matrix, played)
        return max(cols, key=lambda c: (matrix["payoffs"][predicted][c][1], -c))
    if policy == "reactive":
        if not played:
            return 0
        last = played[-1]
        return max(cols, key=lambda c: (matrix["payoffs"][last][c][1], -c))
    rows = range(len(matrix["rows"]))
    value = {c: sum(played.count(r) * matrix["payoffs"][r][c][1] for r in rows) for c in cols}
    return max(cols, key=lambda c: (value[c], -c))


def duel_predicted_row(matrix, played):
    """The row the exploiter expects next: what you most often play after your last row, or your most
    common row when that sequence has not happened yet. The first row is expected first."""
    if not played:
        return 0
    last = played[-1]
    pool = [played[i + 1] for i in range(len(played) - 1) if played[i] == last] or played
    rows = range(len(matrix["rows"]))
    return max(rows, key=lambda r: (pool.count(r), -r))


def duel_best_row(matrix, col):
    """Your best row against a column: the first row that does best for you."""
    rows = range(len(matrix["rows"]))
    return max(rows, key=lambda r: (matrix["payoffs"][r][col][0], -r))


def _play_duel(game, catalog, ask, say):
    match = next((item for item in catalog if item["id"] == game["game"]), None)
    if match is None or not match.get("matrix"):
        say(f"No payoff table for '{game['game']}'.")
        return
    matrix = match["matrix"]
    rows = matrix["rows"]
    say(f"Enter the number of your row, 1 to {len(rows)}. h for a hint, q quits.")
    played, you, engine = [], 0, 0
    round_number = 1
    while round_number <= game["rounds"]:
        line = _read(ask, f"Round {round_number} (row 1 to {len(rows)}): ")
        if line is None:
            say("You left the game.")
            return
        if line == "h":
            col = duel_engine_col(matrix, played, game["policy"])
            say(f"Hint: the engine will play {matrix['cols'][col]}. {rows[duel_best_row(matrix, col)]} does best against that.")
            continue
        if not (line.isdigit() and 1 <= int(line) <= len(rows)):
            say(f"Enter a row number from 1 to {len(rows)}.")
            continue
        row = int(line) - 1
        col = duel_engine_col(matrix, played, game["policy"])
        played.append(row)
        u, v = matrix["payoffs"][row][col]
        you += u
        engine += v
        say(f"You played {rows[row]}, the engine played {matrix['cols'][col]}. You get {u}, it gets {v}.")
        round_number += 1
    say(f"Final score: you {you}, the engine {engine}.")
    say("You win the match." if you > engine else "The engine wins the match." if engine > you else "The match is drawn.")

