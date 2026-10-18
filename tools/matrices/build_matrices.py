"""Add payoff tables (normal forms) to games that lack one.

Each table is either:
  exact       - computed from the game's stated rules, or the standard textbook form
  simplified  - an illustrative form we chose to show the structure; the numbers are not from data

Every table carries a note saying which it is. Run from the project root:

    python3 tools/matrices/build_matrices.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "gtplaybook" / "data"
GAME_FILES = ["games.json", "more-games.json", "families-games.json", "work-and-business.json",
              "government.json", "society.json", "games-and-puzzles.json", "intelligence.json",
              "advanced-games.json", "additional-games.json"]

EXACT = "exact: computed from the rules of the game, or its standard textbook form"
SIMPLIFIED = "simplified: an illustrative form that shows the structure; the numbers are chosen, not measured"


def table(rows, cols, payoffs, note):
    for row in payoffs:
        for cell in row:
            for value in cell:
                if not isinstance(value, int):
                    raise ValueError(f"payoffs must be whole numbers, got {value!r} for {note[:40]}")
    return {"rows": rows, "cols": cols, "payoffs": payoffs, "note": note}


def two_by_two(rows, cols, cells, note):
    """cells in reading order: [(r0c0), (r0c1)], [(r1c0), (r1c1)] as (your, their) pairs."""
    return table(rows, cols, [[list(c) for c in row] for row in cells], note)


def rock_paper_scissors():
    names = ["Rock", "Paper", "Scissors"]
    beats = {("Rock", "Scissors"), ("Paper", "Rock"), ("Scissors", "Paper")}
    payoffs = []
    for a in names:
        row = []
        for b in names:
            if a == b:
                row.append([0, 0])
            elif (a, b) in beats:
                row.append([1, -1])
            else:
                row.append([-1, 1])
        payoffs.append(row)
    return table(names, names, payoffs, EXACT)


def travelers_dilemma():
    claims = [2, 3, 4]
    reward = 2
    payoffs = []
    for a in claims:
        row = []
        for b in claims:
            if a == b:
                row.append([a, b])
            elif a < b:
                row.append([a + reward, a - reward])
            else:
                row.append([b - reward, b + reward])
        payoffs.append(row)
    return table([f"Claim {c}" for c in claims], [f"Claim {c}" for c in claims], payoffs,
                 EXACT + " (a shortened version: claims 2 to 4, reward and penalty 2)")


def colonel_blotto():
    """Asymmetric Blotto: you have three troops, the rival two, and two battlefields.
    Whoever sends more troops to a field wins it. Payoff: fields won minus fields lost."""
    def splits(total):
        return [(a, total - a) for a in range(total, -1, -1)]

    mine, theirs = splits(3), splits(2)

    def score(x, y):
        return sum(1 if p > q else -1 if p < q else 0 for p, q in zip(x, y))

    payoffs = [[[score(x, y), -score(x, y)] for y in theirs] for x in mine]
    return table([f"{a} then {b}" for a, b in mine], [f"{a} then {b}" for a, b in theirs], payoffs,
                 EXACT + " (you have three troops and the rival two, across two battlefields; the stronger force wins each field)")


def hawk_dove():
    value, cost = 2, 4
    hh = (value - cost) // 2
    dd = value // 2
    return two_by_two(["Hawk", "Dove"], ["Hawk", "Dove"], [
        [(hh, hh), (value, 0)],
        [(0, value), (dd, dd)],
    ], EXACT + " (value 2, cost 4, so Hawk against Hawk scores (2 - 4) / 2)")


def sealed_bid_first_price():
    values = (6, 4)
    bids = [2, 4, 6]
    def payoff(own_value, own_bid, other_bid):
        if own_bid > other_bid:
            return own_value - own_bid
        if own_bid == other_bid:
            return (own_value - own_bid) // 2
        return 0
    payoffs = []
    for b in bids:
        payoffs.append([[payoff(values[0], b, c), payoff(values[1], c, b)] for c in bids])
    labels = [f"Bid {b}" for b in bids]
    return table(labels, labels, payoffs,
                 EXACT + " (first-price sealed bid; values 6 and 4; ties split the surplus)")


def median_voter():
    positions = [0, 1, 2]
    names = ["Left", "Centre", "Right"]
    voters = [0, 1, 2]

    def result(row, col):
        """+1 if the row candidate wins the vote, -1 if it loses, 0 for a tie. Zero-sum."""
        row_votes = sum(1 for v in voters if abs(v - row) < abs(v - col))
        col_votes = sum(1 for v in voters if abs(v - row) > abs(v - col))
        return (row_votes > col_votes) - (row_votes < col_votes)

    payoffs = []
    for r in positions:
        payoffs.append([[result(r, c), -result(r, c)] for c in positions])
    return table(names, names, payoffs,
                 EXACT + " (three positions, three equal groups of voters; each votes for the nearer candidate)")


def matching_pennies(row_names, col_names, note):
    """A zero-sum game: the first player wins when the choices differ, and the second wins when they match."""
    return two_by_two(row_names, col_names, [
        [(-1, 1), (1, -1)],
        [(1, -1), (-1, 1)],
    ], note)


def keynes_guess():
    """Guess 1, 2 or 3. The target is two thirds of the average guess; the guess closer to it wins 2, a tie gives 1 each."""
    guesses = [1, 2, 3]

    def result(a, b):
        # target = (2/3) * (a + b) / 2 = (a + b) / 3, so compare |a - target| and |b - target| as whole numbers
        da, db = abs(3 * a - (a + b)), abs(3 * b - (a + b))
        if da < db:
            return 2, 0
        if da > db:
            return 0, 2
        return 1, 1

    payoffs = [[list(result(a, b)) for b in guesses] for a in guesses]
    labels = [f"Guess {g}" for g in guesses]
    return table(labels, labels, payoffs,
                 EXACT + " (two players guess 1, 2 or 3; the guess nearest two thirds of the average wins 2, a tie gives 1 each)")


def cournot_quantities():
    """Two firms choose 1, 2 or 3 units at the same time. Price is 10 minus total output (never below 0); cost is zero."""
    quantities = [1, 2, 3]

    def profit(own, other):
        return own * max(0, 10 - (own + other))

    payoffs = [[[profit(a, b), profit(b, a)] for b in quantities] for a in quantities]
    labels = [f"Produce {q}" for q in quantities]
    return table(labels, labels, payoffs,
                 EXACT + " (simultaneous quantity choice with price 10 minus total output; the standard Cournot form, restricted to 1 to 3 units)")


def entry_game():
    rows = ["Stay out", "Enter"]
    cols = ["Fight", "Accommodate"]
    payoffs = [
        [[0, 2], [0, 2]],
        [[-1, -1], [1, 1]],
    ]
    return table(rows, cols, payoffs,
                 EXACT + " (the standard textbook entry game: a threat to fight is not credible if accommodating pays more)")


def vickrey_auction():
    """Second-price sealed-bid auction: the highest bid wins and pays the second-highest bid. Values 6 and 4; ties give 0."""
    values = (6, 4)
    bids = [3, 4, 5, 6]

    def payoff(own_value, own_bid, other_bid):
        if own_bid > other_bid:
            return own_value - other_bid
        return 0

    payoffs = [[[payoff(values[0], a, b), payoff(values[1], b, a)] for b in bids] for a in bids]
    labels = [f"Bid {b}" for b in bids]
    return table(labels, labels, payoffs,
                 EXACT + " (second-price sealed-bid auction with values 6 and 4; bidding your true value is weakly dominant)")



def hotelling_shops():
    """Two shops on a line of customers at 0 to 10, each customer using the nearer shop. Ties split the customers,
    so payoffs are twice the customer count (out of 22), which keeps every payoff a whole number."""
    spots = [2, 5, 8]
    names = ["Open at 2", "Open at 5", "Open at 8"]

    def share(you, them):
        mine = 0
        for customer in range(11):
            d_you, d_them = abs(customer - you), abs(customer - them)
            if d_you < d_them:
                mine += 2
            elif d_you == d_them:
                mine += 1
        return mine

    payoffs = [[[share(a, b), 22 - share(a, b)] for b in spots] for a in spots]
    return table(names, names, payoffs, EXACT + " (customers 0 to 10 use the nearer shop; ties split, and payoffs count customers doubled)")


def nash_demand():
    """Each party demands 4, 5 or 6 of a prize of 10. Both get their demand if the two demands fit, otherwise nothing."""
    demands = [4, 5, 6]
    payoffs = []
    for a in demands:
        row = []
        for b in demands:
            row.append([a, b] if a + b <= 10 else [0, 0])
        payoffs.append(row)
    names = [f"Demand {d}" for d in demands]
    return table(names, names, payoffs, EXACT + " (the discrete Nash demand game; the equal split is the bargaining solution)")


def chicken_signal():
    """Chicken with the standard payoffs: both swerve 3 each, one dares 4 and the other swerves 1, both dare 0 each."""
    return two_by_two(["Swerve", "Dare"], ["Swerve", "Dare"], [
        [(3, 3), (1, 4)],
        [(4, 1), (0, 0)],
    ], EXACT + " (the standard Chicken payoffs; a shared signal can recommend which driver goes)")


DEFINITIONS = {
    "matching-pennies": lambda: matching_pennies(["Heads", "Tails"], ["Heads", "Tails"],
        EXACT + " (the first player wins when the coins differ; the second wins when they match)"),
    "penalty-kicks-and-serves": lambda: matching_pennies(["Shoot left", "Shoot right"], ["Dive left", "Dive right"],
        EXACT + " (the striker scores when the keeper dives the other way)"),
    "dictator-game": lambda: two_by_two(["Split evenly", "Keep everything"], ["Observed", "Unobserved"], [
        [(3, 3), (3, 3)],
        [(5, 0), (2, 0)],
    ], SIMPLIFIED + " (the dictator's payoff falls when the choice is seen and keeping everything is judged badly)"),
    "braess-paradox-traffic": lambda: two_by_two(["Old route", "Shortcut"], ["Old route", "Shortcut"], [
        [(-4, -4), (-4, -2)],
        [(-2, -4), (-6, -6)],
    ], SIMPLIFIED + " (two drivers; a driver takes 2 minutes on the shortcut alone, 6 if both use it, and 4 on the old route; payoffs are minus minutes)"),
    "nash-bargaining-demands": nash_demand,
    "minority-game-crowds": lambda: two_by_two(["Bar A", "Bar B"], ["Bar A", "Bar B"], [
        [(-1, -1), (1, 1)],
        [(1, 1), (-1, -1)],
    ], SIMPLIFIED + " (two players; the one in the less crowded place wins, and both in the same place lose)"),
    "hotelling-shop-location": hotelling_shops,
    "tariff-war-trade-deal": lambda: table(["Keep trade open", "Impose tariffs", "Offer a deal"], ["Keep trade open", "Impose tariffs", "Offer a deal"], [
        [[3, 3], [0, 4], [3, 3]],
        [[4, 0], [1, 1], [2, 2]],
        [[3, 3], [2, 2], [4, 4]],
    ], SIMPLIFIED + " (a tariff gains a short edge over an open partner; mutual tariffs hurt both; a deal pays both best)"),
    "cyber-defence-allocation": lambda: two_by_two(["Harden the critical systems", "Spread effort thinly"], ["Target critical systems", "Target weakest systems"], [
        [(2, -2), (1, 0)],
        [(-3, 3), (-1, 1)],
    ], SIMPLIFIED + " (defender's side only: payoffs are protection values, and the attacker's gain is the defender's loss)"),
    "supply-chain-bullwhip": lambda: two_by_two(["Keep stock lean", "Hold a safety buffer"], ["Order just in time", "Order ahead to be safe"], [
        [(3, 3), (0, 1)],
        [(2, 1), (2, 2)],
    ], SIMPLIFIED + " (the supplier and retailer share the value of steady orders; panic ordering wastes stock)"),
    "parent-teen-curfew-trust": lambda: two_by_two(["Strict curfew", "Flexible curfew"], ["Follow the curfew", "Test the limit"], [
        [(3, 2), (-1, -1)],
        [(2, 3), (-2, -1)],
    ], SIMPLIFIED + " (parent's and teenager's wellbeing; trust and agreement pay both)"),
    "traffic-signal-correlated": chicken_signal,
    "kin-selection-helping-relatives": lambda: two_by_two(["Help the relative", "Keep to yourself"], ["Relative helps", "Relative keeps"], [
        [(6, 6), (1, 5)],
        [(5, 1), (0, 0)],
    ], SIMPLIFIED + " (inclusive fitness with relatedness one-half; helping costs 2 and gives the relative 6)"),
    "beliefs-after-surprise": lambda: two_by_two(["Send the costly signal", "Stay quiet"], ["Trust the signal", "Ignore the signal"], [
        [(2, 2), (0, 1)],
        [(1, 0), (1, 1)],
    ], SIMPLIFIED + " (a strong sender gains from a signal the receiver trusts; a weak sender could not afford to copy it)"),
    "rock-paper-scissors": rock_paper_scissors,
    "travelers-dilemma": travelers_dilemma,
    "colonel-blotto": colonel_blotto,
    "ess-hawk-dove-population": hawk_dove,
    "sealed-bid-auctions": sealed_bid_first_price,
    "median-voter-spatial-competition": median_voter,
    "search-game-hide-and-seek": lambda: matching_pennies(
        ["Hide in A", "Hide in B"], ["Search A", "Search B"],
        EXACT + " (the hider wins if the searcher does not look where it hides)"),
    "surprise-and-reconnaissance": lambda: matching_pennies(
        ["Strike A", "Strike B"], ["Guard A", "Guard B"],
        EXACT + " (the attacker wins if the defender guards the other target)"),
    "bank-run": lambda: two_by_two(["Wait", "Withdraw early"], ["Wait", "Withdraw early"], [
        [(2, 2), (0, 1)],
        [(1, 0), (1, 1)],
    ], SIMPLIFIED + " (waiting pays 2 if the other depositor waits, and 0 if they withdraw)"),
    "algorithmic-collusion": lambda: two_by_two(["Price high", "Price low"], ["Price high", "Price low"], [
        [(3, 3), (0, 5)],
        [(5, 0), (1, 1)],
    ], SIMPLIFIED + " (one-shot pricing: matching the high price earns 3 each; undercutting earns 5)"),
    "repeated-prisoners-dilemma": lambda: two_by_two(["Cooperate", "Defect"], ["Cooperate", "Defect"], [
        [(3, 3), (0, 5)],
        [(5, 0), (1, 1)],
    ], EXACT + " (the one-shot prisoner's dilemma that the repeated game is built from)"),
    "plea-bargaining": lambda: two_by_two(["Confess", "Stay silent"], ["Confess", "Stay silent"], [
        [(-5, -5), (0, -10)],
        [(-10, 0), (-1, -1)],
    ], SIMPLIFIED + " (payoffs are negative years in prison)"),
    "trust-game": lambda: two_by_two(["Trust", "Keep"], ["Reciprocate", "Keep"], [
        [(3, 3), (0, 5)],
        [(1, 1), (1, 0)],
    ], SIMPLIFIED + " (the investor trusts or keeps; the trustee repays or keeps the money)"),
    "tragedy-of-the-commons": lambda: two_by_two(["Restrain", "Exploit"], ["Restrain", "Exploit"], [
        [(3, 3), (1, 4)],
        [(4, 1), (2, 2)],
    ], SIMPLIFIED + " (two herders; exploiting the shared pasture gains you more, and hurts both)"),
    "team-production-shirking": lambda: two_by_two(["Work", "Shirk"], ["Work", "Shirk"], [
        [(3, 3), (0, 4)],
        [(4, 0), (1, 1)],
    ], SIMPLIFIED + " (two workers; shirking gains you more while the other works, and you get nothing when you work alone)"),
    "household-chores-bills": lambda: two_by_two(["Do your share", "Free-ride"], ["Do your share", "Free-ride"], [
        [(2, 2), (0, 3)],
        [(3, 0), (1, 1)],
    ], SIMPLIFIED + " (two housemates; free-riding saves effort at the other's expense)"),
    "insurance-moral-hazard": lambda: two_by_two(["Careful", "Careless"], ["Audit", "Trust"], [
        [(2, 1), (2, 2)],
        [(1, 1), (4, -2)],
    ], SIMPLIFIED + " (insured person takes care or not; the insurer audits or trusts)"),
    "principal-agent": lambda: two_by_two(["Bonus", "Flat pay"], ["Work hard", "Shirk"], [
        [(3, 2), (0, 0)],
        [(1, 1), (0, 1)],
    ], SIMPLIFIED + " (the principal pays a bonus or flat pay; the agent works hard or shirks)"),
    "firing-and-performance": lambda: two_by_two(["Support and keep", "Fire"], ["Improve", "Stay static"], [
        [(3, 3), (0, 2)],
        [(-1, 0), (1, -1)],
    ], SIMPLIFIED + " (the manager keeps and supports, or fires; the employee improves or not)"),
    "hiring-screening": lambda: two_by_two(["Screen first", "Hire untested"], ["Qualified", "Unqualified"], [
        [(3, 3), (1, 0)],
        [(2, 3), (-1, 1)],
    ], SIMPLIFIED + " (the employer screens or hires untested; the candidate is qualified or not)"),
    "whistleblowing": lambda: two_by_two(["Report", "Stay silent"], ["Firm corrects", "Firm covers up"], [
        [(2, 3), (-1, -2)],
        [(1, 2), (0, 0)],
    ], SIMPLIFIED + " (the employee reports or stays silent; the firm corrects or covers up)"),
    "lobbying-influence": lambda: two_by_two(["Lobby", "Do not lobby"], ["Accommodate", "Resist"], [
        [(3, 2), (-1, 0)],
        [(0, 1), (1, 1)],
    ], SIMPLIFIED + " (a firm lobbies or not; the regulator accommodates or resists)"),
    "defending-a-position": lambda: two_by_two(["Attack", "Hold"], ["Reinforce", "Withdraw"], [
        [(-1, 1), (2, -2)],
        [(0, 0), (1, 0)],
    ], SIMPLIFIED + " (the attacker attacks or holds; the defender reinforces or withdraws)"),
    "crisis-negotiation": lambda: two_by_two(["Concede", "Hold firm"], ["Concede", "Hold firm"], [
        [(2, 2), (0, 3)],
        [(3, 0), (-3, -3)],
    ], SIMPLIFIED + " (a chicken-style standoff: holding firm against a concession wins; holding firm against holding firm is a crash)"),
    "emergency-supply-hoarding": lambda: two_by_two(["Buy realistically", "Hoard"], ["Buy realistically", "Hoard"], [
        [(3, 3), (0, 4)],
        [(4, 0), (1, 1)],
    ], SIMPLIFIED + " (hoarding gains you stock while the other buys realistically)"),
    "disaster-preparedness-investment": lambda: two_by_two(["Invest in defences", "Skip"], ["Invest in defences", "Skip"], [
        [(2, 2), (-1, 3)],
        [(3, -1), (0, 0)],
    ], SIMPLIFIED + " (shared defences are a public good: you pay, the neighbour benefits)"),
    "mass-uprising-threshold": lambda: two_by_two(["Join", "Stay home"], ["Join", "Stay home"], [
        [(3, 3), (-1, 0)],
        [(0, -1), (1, 1)],
    ], SIMPLIFIED + " (joining only pays if enough others join: a coordination game)"),
    "elite-defection-coordination": lambda: two_by_two(["Defect", "Stay"], ["Defect", "Stay"], [
        [(3, 3), (0, 1)],
        [(1, 0), (2, 2)],
    ], SIMPLIFIED + " (defecting pays only if others defect too: a coordination game)"),
    "nonviolent-resistance": lambda: two_by_two(["Persist", "Retreat"], ["Accommodate", "Repress"], [
        [(3, 0), (-1, 2)],
        [(1, 2), (0, 1)],
    ], SIMPLIFIED + " (protesters persist or retreat; the regime accommodates or represses)"),
    "intel-warning-problem": lambda: two_by_two(["Warn", "Stay quiet"], ["Act on warning", "Ignore"], [
        [(1, 2), (-1, 1)],
        [(0, 1), (-2, -2)],
    ], SIMPLIFIED + " (an analyst warns or stays quiet; the decision-maker acts on the warning or ignores it)"),
    "information-sharing-alliance": lambda: two_by_two(["Share", "Withhold"], ["Share", "Withhold"], [
        [(3, 3), (0, 2)],
        [(2, 0), (1, 1)],
    ], SIMPLIFIED + " (partners share intelligence or withhold it)"),
    "disclosure-game": lambda: two_by_two(["Disclose", "Conceal"], ["Inspect", "Trust"], [
        [(1, 1), (2, 2)],
        [(-2, 1), (3, 0)],
    ], SIMPLIFIED + " (a firm discloses or conceals; the regulator inspects or trusts)"),
    "alliance-entrapment": lambda: two_by_two(["Support", "Withdraw"], ["Commit", "Abandon"], [
        [(2, 2), (-2, 0)],
        [(0, -1), (1, 1)],
    ], SIMPLIFIED + " (an ally supports or withdraws; the patron commits or abandons)"),
    "siege-and-logistics": lambda: two_by_two(["Besiege", "Assault"], ["Hold", "Sortie"], [
        [(1, 1), (-1, 2)],
        [(2, -1), (0, 0)],
    ], SIMPLIFIED + " (besiegers wait or assault; the defenders hold or sortie)"),
    "keynes-beauty-contest": keynes_guess,
    "stackelberg-leadership": cournot_quantities,
    "subgame-perfection-threats": entry_game,
    "vcg-mechanism-design": vickrey_auction,
    "agenda-setting-voting": lambda: two_by_two(["Put reform first", "Put status quo first"], ["Support", "Oppose"], [
        [(2, 2), (-1, 1)],
        [(1, -1), (0, 0)],
    ], SIMPLIFIED + " (the agenda-setter chooses which motion is voted on first; the voter supports or opposes)"),
    "asymmetric-insurgency": lambda: two_by_two(["Hit and run", "Stand and fight"], ["Patrol", "Mass search"], [
        [(2, -1), (1, 1)],
        [(-1, 2), (-2, 1)],
    ], SIMPLIFIED + " (insurgents strike and withdraw or stand and fight; the government patrols or launches a mass search)"),
    "authoritarian-survival": lambda: two_by_two(["Stay loyal", "Defect"], ["Reward", "Purge"], [
        [(2, 2), (-2, 1)],
        [(1, -2), (-3, -3)],
    ], SIMPLIFIED + " (an elite stays loyal or defects; the leader rewards or purges)"),
    "bayesian-persuasion": lambda: two_by_two(["Reveal fully", "Conceal"], ["Act", "Hold"], [
        [(2, 2), (0, 1)],
        [(1, 0), (0, 1)],
    ], SIMPLIFIED + " (the informed sender reveals or conceals; the receiver acts or holds)"),
    "cake-cutting-fair-division": lambda: two_by_two(["Cut evenly", "Cut unevenly"], ["Take the larger piece", "Take the smaller piece"], [
        [(1, 1), (0, 2)],
        [(2, 0), (1, 1)],
    ], SIMPLIFIED + " (one player cuts the cake; the other chooses the piece)"),
    "coalition-formation": lambda: two_by_two(["Join the coalition", "Go alone"], ["Join the coalition", "Go alone"], [
        [(3, 3), (0, 1)],
        [(1, 0), (1, 1)],
    ], SIMPLIFIED + " (two parties; a coalition pays only if both join)"),
    "contract-incentives-incomplete": lambda: two_by_two(["Specify in contract", "Leave open"], ["Invest", "Hold back"], [
        [(2, 2), (-1, 1)],
        [(1, -1), (0, 0)],
    ], SIMPLIFIED + " (the buyer specifies terms or leaves them open; the supplier invests or holds back)"),
    "cults-coercive-groups": lambda: two_by_two(["Stay", "Leave"], ["Loosen control", "Tighten control"], [
        [(2, 2), (-1, 1)],
        [(0, 0), (1, -1)],
    ], SIMPLIFIED + " (a member stays or leaves; the group loosens or tightens control)"),
    "dating-marriage-market-search": lambda: two_by_two(["Accept the first offer", "Keep searching"], ["Accept the first offer", "Keep searching"], [
        [(2, 2), (0, 1)],
        [(1, 0), (1, 1)],
    ], SIMPLIFIED + " (two people search for a partner; a match is only certain if both accept)"),
    "deception-cheap-talk": lambda: two_by_two(["Tell the truth", "Mislead"], ["Trust", "Verify"], [
        [(2, 2), (0, 1)],
        [(3, -1), (-2, 2)],
    ], SIMPLIFIED + " (a sender tells the truth or misleads; the receiver trusts or verifies, and a lie that is caught costs the sender)"),
    "dollar-auction-escalation": lambda: two_by_two(["Stop bidding", "Raise"], ["Stop bidding", "Raise"], [
        [(0, 0), (-1, 1)],
        [(1, -1), (-2, -2)],
    ], SIMPLIFIED + " (two bidders each stop or raise; raising against a stopper wins, and escalation can cost both)"),
    "double-agent-counterintelligence": lambda: two_by_two(["Monitor", "Act on suspicion"], ["Loyal", "Double"], [
        [(1, 1), (-1, 2)],
        [(0, -1), (2, -2)],
    ], SIMPLIFIED + " (an analytic view only: a service monitors or acts on suspicion; the source is loyal or working for the other side)"),
    "global-games-coordination": lambda: two_by_two(["Invest", "Hold"], ["Invest", "Hold"], [
        [(2, 2), (-1, 1)],
        [(1, -1), (0, 0)],
    ], SIMPLIFIED + " (investors coordinate when fundamentals are strong; a threshold decides)"),
    "herding-cascades": lambda: two_by_two(["Follow the crowd", "Decide privately"], ["Follow the crowd", "Decide privately"], [
        [(2, 2), (0, 1)],
        [(1, 0), (1, 1)],
    ], SIMPLIFIED + " (two agents with private information; following pays when others follow)"),
    "lanchester-combat": lambda: two_by_two(["Concentrate forces", "Spread forces"], ["Concentrate forces", "Spread forces"], [
        [(0, 0), (2, -1)],
        [(-1, 2), (1, 1)],
    ], SIMPLIFIED + " (two forces; concentrating forces wins a battle against a spread force)"),
    "liars-dice": lambda: two_by_two(["Bluff", "Bid honestly"], ["Call", "Believe"], [
        [(1, -1), (-1, 1)],
        [(-1, 1), (1, -1)],
    ], SIMPLIFIED + " (a simplified bluff against a call: the bluffer wins when the caller believes, and the caller wins when bluffing is called)"),
    "matching-markets": lambda: two_by_two(["Propose to top choice", "Propose to second choice"], ["Accept", "Reject"], [
        [(2, 2), (0, 0)],
        [(1, 1), (1, 1)],
    ], SIMPLIFIED + " (a proposer and a receiver match when both agree)"),
    "pandemic-quarantine-game": lambda: two_by_two(["Strict restrictions", "Relax early"], ["Comply", "Defy"], [
        [(2, 2), (-2, 1)],
        [(1, -2), (-1, -1)],
    ], SIMPLIFIED + " (government sets strict or relaxed rules; the public complies or defies)"),
    "poker-bluffing": lambda: two_by_two(["Bet with a bluff", "Check with a weak hand"], ["Call", "Fold"], [
        [(1, -1), (-1, 1)],
        [(-1, 1), (0, 0)],
    ], SIMPLIFIED + " (a simplified bluffing game: a bet is called or folded to)"),
    "promotion-tournament": lambda: two_by_two(["High effort", "Low effort"], ["High effort", "Low effort"], [
        [(2, 2), (0, 3)],
        [(3, 0), (1, 1)],
    ], SIMPLIFIED + " (two employees compete for one promotion; high effort against low effort wins it)"),
    "reputation-reviews": lambda: two_by_two(["Deliver quality", "Cut corners"], ["Review honestly", "Skip review"], [
        [(2, 2), (2, 1)],
        [(0, -2), (0, 0)],
    ], SIMPLIFIED + " (a seller delivers quality or cuts corners; a buyer reviews honestly or does not review)"),
    "signaling-game": lambda: two_by_two(["Get the credential", "Skip it"], ["Pay high wage", "Pay low wage"], [
        [(1, 2), (-1, 1)],
        [(0, 0), (1, 0)],
    ], SIMPLIFIED + " (a worker signals ability with a credential; the employer pays a high or low wage)"),
    "testing-contact-tracing": lambda: two_by_two(["Join testing", "Stay out"], ["Privacy-safe tracing", "Data-heavy tracing"], [
        [(2, 2), (1, -1)],
        [(0, 0), (-1, 1)],
    ], SIMPLIFIED + " (people join testing or stay out; the government traces with privacy safeguards or heavy data use)"),
    "veto-players-reform": lambda: two_by_two(["Propose a large reform", "Propose a small reform"], ["Accept", "Block"], [
        [(2, 2), (-1, 1)],
        [(1, -1), (1, 0)],
    ], SIMPLIFIED + " (a reformer proposes a large or small change; a veto player accepts or blocks)"),
    "lemons-market": lambda: two_by_two(["Pay high price", "Pay low price"], ["Sell good", "Sell bad"], [
        [(3, 2), (-2, 3)],
        [(-1, 2), (1, 1)],
    ], SIMPLIFIED + " (buyers pay high or low; sellers offer good or bad goods)"),
}


_loaded = {}


def load(path):
    """Each file is read once, so every change to it is kept until the file is written."""
    if path not in _loaded:
        _loaded[path] = json.loads(path.read_text(encoding="utf-8"))
    return _loaded[path]


REDUCED_NOTE = (" (a reduced form: a two-choice model of the key decision in this game; it is a different, "
                "smaller game from the original, which the simulation plays move by move)")

DEFINITIONS_REDUCED = {
    "ai-opponent-exploitation": lambda: two_by_two(["Exploit its habit", "Play the equilibrium"], ["Bot repeats", "Bot adapts"], [
        [(3, 1), (1, 0)],
        [(2, 2), (2, 2)],
    ], SIMPLIFIED + REDUCED_NOTE),
    "ai-self-play-learning": lambda: two_by_two(["Learn to cooperate", "Learn to defect"], ["Learn to cooperate", "Learn to defect"], [
        [(3, 3), (0, 5)],
        [(5, 0), (1, 1)],
    ], SIMPLIFIED + REDUCED_NOTE),
    "analysis-bayesian-updating": lambda: two_by_two(["Update on the evidence", "Ignore the evidence"], ["Evidence strong", "Evidence weak"], [
        [(2, 1), (0, 0)],
        [(1, 0), (1, 2)],
    ], SIMPLIFIED + REDUCED_NOTE),
    "centipede-game": lambda: two_by_two(["Stop now", "Continue"], ["Opponent continues", "Opponent stops"], [
        [(2, 2), (2, 2)],
        [(0, 3), (1, 1)],
    ], SIMPLIFIED + REDUCED_NOTE),
    "chess-minimax": lambda: two_by_two(["Attack", "Develop"], ["Opponent defends", "Opponent counterattacks"], [
        [(1, 1), (-1, 2)],
        [(0, 0), (1, 1)],
    ], SIMPLIFIED + REDUCED_NOTE),
    "explore-exploit-bandit": lambda: two_by_two(["Explore a new option", "Exploit the known option"], ["New option is good", "New option is poor"], [
        [(2, 0), (0, 0)],
        [(1, 1), (1, 1)],
    ], SIMPLIFIED + REDUCED_NOTE),
    "folk-theorem-cooperation": lambda: two_by_two(["Cooperate", "Defect"], ["Cooperate", "Defect"], [
        [(3, 3), (0, 5)],
        [(5, 0), (1, 1)],
    ], EXACT + " (the one-shot prisoner's dilemma whose repetition sustains cooperation; the folk theorem depends on patience)"),
    "nim": lambda: two_by_two(["Leave an even pile count", "Leave an odd pile count"], ["Opponent leaves even", "Opponent leaves odd"], [
        [(1, 1), (-1, -1)],
        [(-1, -1), (1, 1)],
    ], SIMPLIFIED + REDUCED_NOTE),
    "rubinstein-bargaining": lambda: two_by_two(["Offer a fair split", "Offer a greedy split"], ["Accept", "Reject"], [
        [(2, 2), (0, 0)],
        [(3, 1), (0, 0)],
    ], SIMPLIFIED + REDUCED_NOTE),
    "secretary-problem": lambda: two_by_two(["Accept the candidate now", "Wait for a better one"], ["Candidate is good", "Candidate is poor"], [
        [(2, 1), (0, 0)],
        [(1, 1), (2, 0)],
    ], SIMPLIFIED + REDUCED_NOTE),
    "shapley-value-sharing": lambda: two_by_two(["Form the coalition", "Go alone"], ["Partner joins", "Partner goes alone"], [
        [(2, 2), (0, 0)],
        [(0, 0), (1, 1)],
    ], SIMPLIFIED + REDUCED_NOTE),
    "tic-tac-toe-minimax": lambda: two_by_two(["Take the centre", "Take a corner"], ["Opponent blocks", "Opponent ignores"], [
        [(0, 0), (-1, 1)],
        [(1, -1), (-2, 2)],
    ], SIMPLIFIED + REDUCED_NOTE),
    "voting-paradoxes": lambda: two_by_two(["Vote for A first", "Vote for B first"], ["Ranking one", "Ranking two"], [
        [(1, 1), (-1, -1)],
        [(-1, -1), (1, 1)],
    ], SIMPLIFIED + REDUCED_NOTE),
}

# Games with no table at all: none remain. Add a reason here only for a game that truly cannot have one.
UNAVAILABLE = {}


def find_game_file(game_id):
    for name in GAME_FILES:
        path = DATA / name
        if not path.exists():
            continue
        data = load(path)
        items = data.get("games", data) if isinstance(data, dict) else data
        for game in items:
            if isinstance(game, dict) and game.get("id") == game_id:
                return path, data, game
    return None, None, None


def main():
    updated, missing = 0, []
    touched = {}
    for game_id, reason in UNAVAILABLE.items():
        path, data, game = find_game_file(game_id)
        if game is None:
            missing.append(game_id)
            continue
        if not game.get("matrix") and game.get("matrix_unavailable") != reason:
            game["matrix_unavailable"] = reason
            touched[path] = data
    for game_id, make in list(DEFINITIONS.items()) + list(DEFINITIONS_REDUCED.items()):
        path, data, game = find_game_file(game_id)
        if game is None:
            missing.append(game_id)
            continue
        if game.get("matrix"):
            continue
        spec = make()
        game["matrix"] = {"rows": spec["rows"], "cols": spec["cols"], "payoffs": spec["payoffs"]}
        game["matrix_note"] = spec["note"]
        game.pop("matrix_unavailable", None)
        touched[path] = data
        updated += 1
    for path, data in touched.items():
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"added {updated} payoff tables")
    if missing:
        print("not found in data files:", ", ".join(missing), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
