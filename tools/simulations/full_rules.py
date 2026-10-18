"""Simulations built from complete rules: tic-tac-toe, Nim, depth-limited Connect Four and a
repeated prisoner's dilemma with bots that remember the game so far.

Each function returns a spec for state_games.build_state_game. Opponents that play perfectly
are deterministic (one reply with probability 1.0); opponents that play at random are uniform.
"""

from functools import lru_cache

# ---------- Tic-tac-toe ----------

LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]


def ttt_winner(board):
    for a, b, c in LINES:
        if board[a] != "." and board[a] == board[b] == board[c]:
            return board[a]
    return None


def ttt_turn(board):
    return "X" if board.count("X") == board.count("O") else "O"


def ttt_show(board):
    return "/".join(board[r * 3:r * 3 + 3] for r in range(3))


def ttt_place(board, i, mark):
    return board[:i] + mark + board[i + 1:]


@lru_cache(maxsize=None)
def ttt_value(board):
    """Score for X with both sides playing perfectly: 1 win, 0 draw, -1 loss."""
    won = ttt_winner(board)
    if won == "X":
        return 1
    if won == "O":
        return -1
    if "." not in board:
        return 0
    mark = ttt_turn(board)
    values = [ttt_value(ttt_place(board, i, mark)) for i, c in enumerate(board) if c == "."]
    return max(values) if mark == "X" else min(values)


def ttt_why_move(board, i):
    after = ttt_place(board, i, "X")
    if ttt_winner(after) == "X":
        return "Completes a line of three and wins."
    if ttt_winner(ttt_place(board, i, "O")) == "O":
        return "Blocks the opponent's winning line."
    threats = [j for j, c in enumerate(after) if c == "." and ttt_winner(ttt_place(after, j, "X")) == "X"]
    if len(threats) >= 2:
        return "Creates two winning threats at once, a fork the opponent cannot block."
    if i == 4:
        return "The centre lies on four lines, more than any other square."
    if i in (0, 2, 6, 8):
        return "A corner lies on three lines and gives the most chances to build threats."
    return "An edge lies on only two lines, so it creates the fewest threats."


def ttt_perfect_reply(board):
    """The perfect opponent's reply: the square that gives X the least, lowest index on ties."""
    empties = [i for i, c in enumerate(board) if c == "."]
    best = min(empties, key=lambda i: (ttt_value(ttt_place(board, i, "O")), i))
    return best


def ttt_why_reply(board, i):
    after = ttt_place(board, i, "O")
    if ttt_winner(after) == "O":
        return "Takes a winning line."
    if ttt_winner(ttt_place(board, i, "X")) == "X":
        return "Blocks your winning line."
    value = ttt_value(after)
    result = {1: "a win for you", 0: "a draw", -1: "a loss for you"}[value]
    return f"Plays the best reply; with perfect play from here the game is {result}."


def ttt_spec(sim_id, name, summary, perfect):
    def player(board):
        out = []
        for i, c in enumerate(board):
            if c == ".":
                out.append((f"Take square {i + 1}", ttt_why_move(board, i), ttt_place(board, i, "X")))
        return out

    def opponent(board):
        empties = [i for i, c in enumerate(board) if c == "."]
        if perfect:
            i = ttt_perfect_reply(board)
            return [(1.0, f"Opponent takes square {i + 1}", ttt_why_reply(board, i), ttt_place(board, i, "O"))]
        p = 1.0 / len(empties)
        return [(p, f"Opponent takes square {i + 1}",
                 "The opponent picks one square at random, so each empty square is equally likely.",
                 ttt_place(board, i, "O")) for i in empties]

    def result(board):
        won = ttt_winner(board)
        if won == "X":
            return "victory", "You completed a line of three."
        if won == "O":
            return "failure", "The opponent completed a line of three."
        if "." not in board:
            return "draw", "The board filled with no line."
        return None

    return {
        "id": sim_id,
        "name": name,
        "families": ["Traditional and parlour games", "Games against AI", "Classic game theory"],
        "summary": summary,
        "start": "." * 9,
        "player": player,
        "opponent": opponent,
        "result": result,
        "prompt": lambda board: f"Your move as X. Board (rows separated by /): {ttt_show(board)}",
        "opp_prompt": lambda board: f"The opponent answers. Board: {ttt_show(board)}",
    }


# ---------- Nim ----------


def nim_sum(piles):
    total = 0
    for p in piles:
        total ^= p
    return total


def nim_spec(sim_id, name, start, perfect, summary):
    def canon(piles):
        return tuple(sorted(piles))

    def player(state):
        piles, _ = state
        out = []
        for idx, size in enumerate(piles):
            for take in range(1, size + 1):
                nxt = list(piles)
                nxt[idx] -= take
                after = canon(nxt)
                if nim_sum(after) == 0:
                    why = "Leaves nim-sum zero: whatever the opponent takes, you can answer and keep it balanced."
                else:
                    why = "Leaves a position with nim-sum not zero, which gives the opponent a winning reply."
                if sum(after) == 0:
                    why = "Takes the last stones, so you win under normal play."
                out.append((f"Take {take} from pile {size}", why, (after, "O")))
        return out

    def opponent(state):
        piles, _ = state
        moves = []
        for idx, size in enumerate(piles):
            for take in range(1, size + 1):
                nxt = list(piles)
                nxt[idx] -= take
                moves.append((canon(nxt), idx, take))
        if perfect:
            balanced = [m for m in moves if nim_sum(m[0]) == 0]
            chosen = balanced[0] if balanced else moves[0]
            after, idx, take = chosen
            why = ("The perfect opponent restores nim-sum zero." if balanced
                   else "No move restores nim-sum zero, so the opponent takes one stone.")
            return [(1.0, f"Opponent takes {take} from pile {piles[idx]}", why, (after, "P"))]
        p = 1.0 / len(moves)
        return [(p, f"Opponent takes {take} from pile {piles[idx]}",
                 "The opponent picks a move at random.", (after, "P"))
                for after, idx, take in moves]

    def result(state):
        piles, to_move = state
        if sum(piles) > 0:
            return None
        if to_move == "O":
            return "victory", "You took the last stones, so you win."
        return "failure", "The opponent took the last stones, so you lose."

    return {
        "id": sim_id,
        "name": name,
        "families": ["Traditional and parlour games", "Games against AI", "Classic game theory"],
        "summary": summary,
        "start": (canon(start), "P"),
        "player": player,
        "opponent": opponent,
        "result": result,
        "prompt": lambda state: "Piles " + ", ".join(str(p) for p in state[0]) + ". Your move.",
        "opp_prompt": lambda state: "Piles " + ", ".join(str(p) for p in state[0]) + ". The opponent moves.",
    }


# ---------- Connect Four, depth-limited ----------

ROWS, COLS = 6, 7
WINDOWS = []
for r in range(ROWS):
    for c in range(COLS):
        for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
            cells = [(r + k * dr, c + k * dc) for k in range(4)]
            if all(0 <= rr < ROWS and 0 <= cc < COLS for rr, cc in cells):
                WINDOWS.append([rr * COLS + cc for rr, cc in cells])


def c4_winner(board):
    for cells in WINDOWS:
        marks = {board[i] for i in cells}
        if len(marks) == 1 and "." not in marks:
            return marks.pop()
    return None


def c4_drop(board, col, mark):
    for row in range(ROWS - 1, -1, -1):
        idx = row * COLS + col
        if board[idx] == ".":
            return board[:idx] + mark + board[idx + 1:], row
    return None, None


def c4_score(board, mark):
    """Open windows of four for one mark, weighted by how full they are (2 marks: 1, 3 marks: 3).
    A window with an opponent piece in it is closed. Works from the first few moves, unlike a
    count of threats, which needs three pieces in one window."""
    other = "O" if mark == "X" else "X"
    total = 0
    for cells in WINDOWS:
        marks = [board[i] for i in cells]
        if other in marks:
            continue
        held = marks.count(mark)
        if held >= 2:
            total += 1 if held == 2 else 3
    return total


def c4_show(board):
    return "/".join(board[r * COLS:(r + 1) * COLS] for r in range(ROWS))


def c4_spec(sim_id, name, depth, summary):
    """Player X moves first; a random opponent replies. After `depth` moves by you, the game stops and
    the position is judged by open lines of four, a shallow look ahead rather than a full solve."""

    def player(state):
        board, made = state
        out = []
        for col in range(COLS):
            nxt, row = c4_drop(board, col, "X")
            if nxt is None:
                continue
            if c4_winner(nxt) == "X":
                why = "Connects four and wins."
            elif c4_score(nxt, "X") > c4_score(nxt, "O"):
                why = "Keeps more open lines of four than the opponent, which gives you the better position."
            elif col == COLS // 2:
                why = "The centre column lies in the most windows of four."
            else:
                why = "Edge columns lie in fewer windows of four, so they help less."
            out.append((f"Drop in column {col + 1}", why, (nxt, made + 1)))
        return out

    def opponent(state):
        board, made = state
        columns = [col for col in range(COLS) if board[col] == "."]
        p = 1.0 / len(columns)
        out = []
        for col in columns:
            nxt, _ = c4_drop(board, col, "O")
            out.append((p, f"Opponent drops in column {col + 1}",
                        "The opponent plays a column at random.", (nxt, made)))
        return out

    def result(state):
        board, made = state
        won = c4_winner(board)
        if won == "X":
            return "victory", "You connected four."
        if won == "O":
            return "failure", "The opponent connected four."
        if "." not in board:
            return "draw", "The board filled with no four in a row."
        if made >= depth and board.count("X") == board.count("O"):
            x, o = c4_score(board, "X"), c4_score(board, "O")
            if x > o:
                return "victory", f"Depth limit reached: your open lines score {x} against the opponent's {o}."
            if o > x:
                return "failure", f"Depth limit reached: the opponent's open lines score {o} against your {x}."
            return "draw", f"Depth limit reached: open lines level at {x} each."
        return None

    empty = "." * (ROWS * COLS)
    return {
        "id": sim_id,
        "name": name,
        "families": ["Traditional and parlour games", "Games against AI"],
        "summary": summary,
        "start": (empty, 0),
        "player": player,
        "opponent": opponent,
        "result": result,
        "prompt": lambda state: f"Your move as X (move {state[1] + 1} of {depth}). Board: {c4_show(state[0])}",
        "opp_prompt": lambda state: f"The opponent replies. Board: {c4_show(state[0])}",
    }


# ---------- Repeated prisoner's dilemma with memory ----------

PD_PAYOFF = {("C", "C"): 3, ("C", "D"): 0, ("D", "C"): 5, ("D", "D"): 1}


def bot_tit_for_tat(prefix):
    """Cooperates first, then copies your previous move. Needs memory of one round."""
    return "C" if not prefix else prefix[-1]


def bot_pattern(prefix):
    """Cooperates, cooperates, then defects; the cycle repeats. Only memory of the whole game reveals it."""
    return "D" if len(prefix) % 3 == 2 else "C"


def bot_grim(prefix):
    """Cooperates until you defect once, then defects for the rest of the game."""
    return "D" if "D" in prefix else "C"


def pd_bot_moves(history, bot):
    return [bot(history[:k]) for k in range(len(history))]


def pd_spec(sim_id, name, rounds, bot, win, draw, summary, families):
    """The state is your history of moves. The bot answers from the same history, so the tree is exact:
    the way to score well is to learn the bot's rule from what you have seen."""

    def player(history):
        bots = pd_bot_moves(history, bot)
        last_bot = bots[-1] if bots else None
        out = []
        for me in "CD":
            if me == "C":
                if last_bot == "D":
                    why = "The bot defected last round; cooperating now risks being exploited again."
                else:
                    why = "Keeps cooperation going: two cooperators each get 3."
            else:
                if last_bot == "C" or last_bot is None:
                    why = "Takes the 5 if the bot cooperates, but the bot may retaliate next round."
                else:
                    why = "Defecting against a defector scores 1 each: the mutual punishment outcome."
            out.append((f"Choose {'cooperate' if me == 'C' else 'defect'}", why, history + (me,)))
        return out

    def opponent(history):
        reply = bot(history[:-1])
        if reply == "C":
            why = "The bot cooperates here, from its own rule and the moves you have made."
        else:
            why = "The bot defects here, from its own rule and the moves you have made."
        return [(1.0, f"Bot {'cooperates' if reply == 'C' else 'defects'}", why, history)]

    def result(history):
        if len(history) < rounds:
            return None
        score = sum(PD_PAYOFF[(me, bo)] for me, bo in zip(history, pd_bot_moves(history, bot)))
        if score >= win:
            return "victory", f"Score {score} over {rounds} rounds: you learned the bot's rule and used it."
        if score >= draw:
            return "draw", f"Score {score} over {rounds} rounds: a fair result against this bot."
        return "failure", f"Score {score} over {rounds} rounds: the bot out-scored you."

    return {
        "id": sim_id,
        "name": name,
        "families": families,
        "summary": summary,
        "start": (),
        "player": player,
        "opponent": opponent,
        "result": result,
        "prompt": lambda history: f"Round {len(history) + 1} of {rounds}. Your moves so far: {''.join(history) or 'none'}.",
        "opp_prompt": lambda history: f"The bot answers in round {len(history)} of {rounds}.",
    }


# ---------- The full-rules catalogue ----------

FULL_RULES = [
    ttt_spec("tic-tac-toe-random-opponent", "Tic-Tac-Toe Against a Random Opponent",
             "Complete rules: every square, every line. The opponent picks any empty square at random, so you can win; the best plan keeps your chances of a win highest.",
             perfect=False),
    ttt_spec("tic-tac-toe-perfect-opponent", "Tic-Tac-Toe Against a Perfect Opponent",
             "Complete rules against an opponent who always finds the best reply. With best play from both sides the game is a draw; the plan shows how to keep it there.",
             perfect=True),
    nim_spec("nim-random-opponent", "Nim: Three Piles Against a Random Opponent", (3, 4, 5), False,
             "Take stones from piles; whoever takes the last stone wins. Balanced positions (nim-sum zero) win for the player who makes them against any reply."),
    nim_spec("nim-perfect-reference", "Nim: Larger Piles Against a Perfect Opponent", (5, 7, 9), True,
             "Larger piles, perfect opponent. The reference is nim-sum: you win from any position where the nim-sum is not zero by moving to nim-sum zero."),
    c4_spec("connect-four-depth-three", "Connect Four, Three-Move Look-Ahead",
            3, "Full 7x6 Connect Four board against a random opponent, with a depth limit of three moves for you. The game stops at the limit and is judged by open lines of four: a shallow look ahead, not a full solve."),
    pd_spec("repeated-pd-pattern-bot", "Ten Rounds Against a Patterned Bot", 10, bot_pattern, 34, 24,
            "Ten rounds of prisoner's dilemma. The bot cooperates twice and defects once, on a repeating cycle. You score by learning the cycle from what you have seen.",
            ["Classic game theory", "Games against AI"]),
    pd_spec("repeated-pd-grim-bot", "Ten Rounds Against a Grim Bot", 10, bot_grim, 30, 14,
            "Ten rounds against a bot that cooperates until you defect once, then defects forever. One defection costs you every later round, so the question is how much you gain before the punishment.",
            ["Classic game theory", "Games against AI"]),
    pd_spec("repeated-pd-tit-for-tat-bot", "Ten Rounds Against a Tit-for-Tat Bot", 10, bot_tit_for_tat, 30, 20,
            "Ten rounds against a bot that copies your last move. Exploiting it for one round costs you the next, so cooperating steadily is the strong plan.",
            ["Classic game theory", "Games against AI"]),
]
