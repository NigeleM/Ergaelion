"""One-off generator: builds data/simulations.json from state-based definitions.

Each simulation is described by a state type. The builder walks every reachable
state and writes it out as a node: an 'end' node (outcome), a 'nature' node
(chance branches) or a 'player' node (options). The output is plain JSON that
the playbook engine reads, so it can be edited by hand afterwards.
"""

import json
import sys
from pathlib import Path


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def build(defn):
    ids, order, nodes = {}, [], {}

    def nid(state):
        if state not in ids:
            ids[state] = f"n{len(ids)}"
            order.append(state)
        return ids[state]

    start = nid(defn["initial"])
    i = 0
    while i < len(order):
        state = order[i]
        i += 1
        key = ids[state]
        term = defn["terminal"](state)
        if term:
            nodes[key] = {"type": "end", "outcome": term[0], "text": term[1]}
            continue
        branches = defn["nature"](state)
        if branches:
            nodes[key] = {
                "type": "nature",
                "prompt": defn["nature_prompt"](state),
                "branches": [
                    {"p": round(p, 4), "label": label, "next": nid(nxt)}
                    for p, label, nxt in branches
                ],
            }
            assert abs(sum(p for p, _, _ in branches) - 1.0) < 1e-6, state
            continue
        nodes[key] = {
            "type": "player",
            "prompt": defn["prompt"](state),
            "options": [{"label": label, "next": nid(nxt)} for label, nxt in defn["options"](state)],
        }
    return {"start": start, "nodes": nodes}


# ---- 1. Salary negotiation -------------------------------------------------

def salary():
    def terminal(s):
        if s[0] == "agree":
            return ("victory" if s[1] >= 60 else "draw", f"Agreed at {s[1]}k.")
        if s[0] == "walk":
            return ("failure", "You walk away with no offer.")
        if s[0] == "end":
            return (s[1], s[2])
        return None

    def nature(s):
        if s[0] == "nat70":
            return [(0.5, "Budget is 60k", ("counter", 60)), (0.5, "Budget is 75k", ("agree", 70))]
        return None

    def options(s):
        if s[0] == "ask":
            return [("Ask 50k", ("agree", 50)), ("Ask 60k", ("agree", 60)), ("Ask 70k", ("nat70",))]
        return [("Accept 60k", ("agree", 60)), ("Walk away", ("walk",))]

    return {
        "id": "salary-negotiation",
        "name": "Salary Negotiation",
        "family": "Work games",
        "summary": "You have a job offer and ask for a salary. The employer has a budget you cannot see. Ask too low and you lose money; ask too high and you risk losing the offer.",
        "initial": ("ask",),
        "terminal": terminal,
        "nature": nature,
        "nature_prompt": lambda s: "The employer checks its budget privately. Chance decides:",
        "prompt": lambda s: "You have an offer. What salary do you ask for?" if s[0] == "ask"
        else "The employer offers 60k. Accept, or walk away?",
        "options": options,
    }


# ---- 2. Repeated prisoner's dilemma against a tit-for-tat bot ---------------

def tit_for_tat():
    pay = {("C", "C"): (3, 3), ("C", "D"): (0, 5), ("D", "C"): (5, 0), ("D", "D"): (1, 1)}
    rounds = 3

    def terminal(s):
        if s[0] == "r" and s[1] > rounds:
            mine, bots = s[2], s[3]
            mine_pts = sum(pay[(m, b)][0] for m, b in zip(mine, bots))
            bot_pts = sum(pay[(m, b)][1] for m, b in zip(mine, bots))
            text = f"You scored {mine_pts} points (the bot scored {bot_pts}). Win at 10 or more, draw at 7 to 9, lose at 6 or fewer."
            if mine_pts >= 10:
                return ("victory", text)
            if mine_pts >= 7:
                return ("draw", text)
            return ("failure", text)
        return None

    def bot_move(s):
        return "C" if s[1] == 1 else s[2][-1]

    def options(s):
        r, mine, bots = s[1], s[2], s[3]
        b = bot_move(s)
        return [
            ("Cooperate", ("r", r + 1, mine + "C", bots + b)),
            ("Defect", ("r", r + 1, mine + "D", bots + b)),
        ]

    def prompt(s):
        r, mine, bots = s[1], s[2], s[3]
        history = ", ".join(f"you {m} / bot {b}" for m, b in zip(mine, bots)) or "none yet"
        return f"Round {r} of {rounds}. History: {history}. Cooperate or defect?"

    return {
        "id": "vs-tit-for-tat",
        "name": "Repeated Game Against a Tit-for-Tat Bot",
        "family": "Games against AI",
        "summary": "Three rounds of the prisoner's dilemma against a bot that cooperates first and then copies your last move. Win with 10 or more points, draw at 7 to 9, lose at 6 or fewer. Notice how the last round changes the best plan.",
        "initial": ("r", 1, "", ""),
        "terminal": terminal,
        "nature": lambda s: None,
        "nature_prompt": lambda s: "",
        "prompt": prompt,
        "options": options,
    }


# ---- 3. Shared fishery over two rounds -------------------------------------

def commons():
    def chance_collapse(both_heavy_count):
        return {2: 0.8, 1: 0.3, 0: 0.05}[both_heavy_count]

    def terminal(s):
        if s[0] == "final":
            if s[1]:
                return ("failure", "The fishery collapses.")
            return ("victory", "The stock survives both seasons.")
        return None

    def nature(s):
        if s[0] != "nature":
            return None
        _, r, mine_now, rival_now, my_h, riv_h = s
        pc = chance_collapse(int(mine_now) + int(rival_now))
        if r == 1:
            survive = ("choose", 2, my_h, riv_h)
        else:
            survive = ("final", False, my_h, riv_h)
        return [
            (pc, "The stock collapses", ("final", True, my_h, riv_h)),
            (1 - pc, "The stock survives", survive),
        ]

    def options(s):
        _, r, my_h, riv_h = s
        rival_now = r == 2
        return [
            ("Sustainable catch", ("nature", r, False, rival_now, my_h, riv_h + int(rival_now))),
            ("Heavy catch", ("nature", r, True, rival_now, my_h + 1, riv_h + int(rival_now))),
        ]

    return {
        "id": "commons-two-seasons",
        "name": "Shared Fishery, Two Seasons",
        "family": "Public goods and environment",
        "summary": "You and a rival fish one lake for two seasons. Each season you choose a sustainable or heavy catch. Heavy catches raise the chance the stock collapses. The rival fishes sustainably in season one and heavily in season two.",
        "initial": ("choose", 1, 0, 0),
        "terminal": terminal,
        "nature": nature,
        "nature_prompt": lambda s: "The season's stock is tested:",
        "prompt": lambda s: f"Season {s[1]} of 2. Sustainable or heavy catch?",
        "options": options,
    }


# ---- 4. Regime survival (illustrative, abstract) ----------------------------

def regime():
    def terminal(s):
        if s[0] == "end":
            return (s[1], s[2])
        return None

    def nature(s):
        if s[0] == "n1":
            p = 0.4
            return [(p, "An economic shock hits", ("c2", s[1], True)),
                    (1 - p, "The economy holds steady", ("c2", s[1], False))]
        if s[0] == "n2":
            _, a1, shock, a2 = s
            pd = 0.1
            pd += {"hold": 0.3, "consult": 0.1}.get(a1, 0.0)
            pd += 0.3 if shock else 0.0
            pd += 0.2 if a2 == "tighten" else 0.0
            pd -= 0.1 if a2 == "reform" else 0.0
            pd = clamp(pd, 0.05, 0.9)
            return [(pd, "Key insiders defect", ("end", "failure", "Key insiders defect and the regime falls.")),
                    (1 - pd, "The regime holds", ("end", "victory", "The regime holds, though it remains fragile."))]
        return None

    def options(s):
        if s[0] == "c1":
            return [("Reward core supporters", ("n1", "reward")),
                    ("Hold back payments", ("n1", "hold")),
                    ("Open limited consultation", ("n1", "consult"))]
        _, a1, shock = s
        return [("Keep rewarding core supporters", ("n2", a1, shock, "reward")),
                ("Tighten control of opposition", ("n2", a1, shock, "tighten")),
                ("Negotiate reforms", ("n2", a1, shock, "reform"))]

    def prompt(s):
        if s[0] == "c1":
            return "Year one. Your core supporters expect payment. What is your approach?"
        return "Year two. Insiders are watching closely. Choose your approach:"

    return {
        "id": "regime-survival",
        "name": "Regime Survival (Two Years)",
        "family": "Government and politics",
        "summary": "An abstract model of an autocrat keeping insiders loyal over two years. The probabilities are illustrative, not measured. The point is to see how rent payments, repression and economic shocks interact, and why visible strain often precedes defection.",
        "initial": ("c1",),
        "terminal": terminal,
        "nature": nature,
        "nature_prompt": lambda s: "Economic conditions and insider reactions:" if s[0] == "n2" else "This year's conditions:",
        "prompt": prompt,
        "options": options,
    }


# ---- 5. Nonviolent campaign ------------------------------------------------

def campaign():
    def terminal(s):
        if s[0] == "end":
            return (s[1], s[2])
        return None

    def nature(s):
        if s[0] == "n1":
            ps = {"broad": 0.6, "elite": 0.2, "wait": 0.1}[s[1]]
            return [(ps, "Turnout surges", ("c2", s[1], "surge")),
                    (1 - ps, "Turnout stays modest", ("c2", s[1], "modest"))]
        if s[0] == "n2":
            _, a1, lvl, a2 = s
            p = 0.1
            p += 0.2 if a1 == "broad" else 0.0
            p += 0.2 if lvl == "surge" else 0.0
            p += 0.1 if a2 == "escalate" else 0.0
            p -= 0.1 if a2 == "compromise" else 0.0
            p = clamp(p, 0.05, 0.6)
            return [
                (p, "Security forces refuse orders", ("end", "victory", "Mass defections force a negotiated transition.")),
                (0.3, "The standoff drags on", ("end", "draw", "Neither side gains; the standoff continues.")),
                (0.7 - p, "The campaign loses momentum", ("end", "failure", "Turnout fades and the demands are dropped.")),
            ]
        return None

    def options(s):
        if s[0] == "c1":
            return [("Broad nonviolent campaign", ("n1", "broad")),
                    ("Narrow elite lobbying", ("n1", "elite")),
                    ("Wait for an opening", ("n1", "wait"))]
        _, a1, lvl = s
        return [("Escalate: wider strikes and outreach to security forces", ("n2", a1, lvl, "escalate")),
                ("Hold steady", ("n2", a1, lvl, "hold")),
                ("Compromise with the regime", ("n2", a1, lvl, "compromise"))]

    def prompt(s):
        if s[0] == "c1":
            return "Your movement must choose a first move. What do you do?"
        return "The first phase ends. Turnout is shown above. What now?"

    return {
        "id": "nonviolent-campaign",
        "name": "Nonviolent Campaign",
        "family": "Government and politics",
        "summary": "Choose how a movement opens and how it develops. Broad participation raises the chance that security forces refuse orders. Narrow tactics stall. The probabilities are illustrative; the research on civil resistance is the reference point.",
        "initial": ("c1",),
        "terminal": terminal,
        "nature": nature,
        "nature_prompt": lambda s: "Participation this phase:" if s[0] == "n1" else "Security forces and the regime respond:",
        "prompt": prompt,
        "options": options,
    }


# ---- 6. Exit from a coercive group ----------------------------------------

def cult_exit():
    def terminal(s):
        if s[0] == "end":
            return (s[1], s[2])
        return None

    def nature(s):
        if s[0] == "n1":
            pp = {"comply": 0.6, "outside": 0.4, "plan": 0.3}[s[1]]
            return [(pp, "The group escalates pressure", ("c2", s[1], "pressure")),
                    (1 - pp, "Things calm down for now", ("c2", s[1], "calm"))]
        if s[0] == "n2":
            _, a1, lvl, a2 = s
            v = 0.2
            v += 0.3 if a1 in ("outside", "plan") else 0.0
            v += 0.3 if a2 == "leave" else 0.0
            v += 0.1 if a2 == "records" else 0.0
            v -= 0.2 if lvl == "pressure" else 0.0
            v -= 0.1 if a2 == "stay" else 0.0
            v = clamp(v, 0.05, 0.8)
            if a1 == "comply" and a2 == "stay":
                f = 0.6
            elif a1 == "comply" or a2 == "stay":
                f = 0.3
            else:
                f = 0.1
            if v + f > 0.95:
                v = 0.95 - f
            d = 1 - v - f
            return [
                (v, "You leave with support and independent help", ("end", "victory", "You leave with support and independent help.")),
                (d, "You stay in contact, unresolved", ("end", "draw", "You remain in contact with the group, and the situation is unresolved.")),
                (f, "Isolation deepens", ("end", "failure", "Isolation deepens and the group's hold tightens.")),
            ]
        return None

    def options(s):
        if s[0] == "c1":
            return [("Comply and say nothing", ("n1", "comply")),
                    ("Talk with an outside person you trust", ("n1", "outside")),
                    ("Quietly plan an exit with a trusted person", ("n1", "plan"))]
        _, a1, lvl = s
        return [("Stay for now", ("n2", a1, lvl, "stay")),
                ("Set a date and leave with support", ("n2", a1, lvl, "leave")),
                ("Ask for written records of money given", ("n2", a1, lvl, "records"))]

    def prompt(s):
        if s[0] == "c1":
            return "The group asks you to hand over savings and stop seeing family. What do you do?"
        return "The group's response is shown above. What is your next step?"

    return {
        "id": "cult-exit-decision",
        "name": "Leaving a Coercive Group",
        "family": "Society and groups",
        "summary": "A member is asked for money and to cut off family. The choices are to comply, to seek outside help, or to plan an exit. Illustrative probabilities, not real statistics. If someone you know is in this situation, a specialist in coercive groups can help.",
        "initial": ("c1",),
        "terminal": terminal,
        "nature": nature,
        "nature_prompt": lambda s: "The group reacts:" if s[0] == "n1" else "The situation develops:",
        "prompt": prompt,
        "options": options,
    }


# ---- 7. Sealed-bid auction against a rival --------------------------------

def auction():
    value = 60

    def terminal(s):
        if s[0] == "resolve":
            _, mine, rival = s
            if mine > rival:
                if mine <= value:
                    return ("victory", f"You win at {mine}k, below your {value}k valuation.")
                return ("failure", f"You win at {mine}k, paying more than the item is worth to you.")
            return ("draw", "You lose the item.")
        return None

    def nature(s):
        if s[0] == "rival":
            mine = s[1]
            return [(0.5, "Rival bids 40k", ("resolve", mine, 40)),
                    (0.5, "Rival bids 65k", ("resolve", mine, 65))]
        return None

    return {
        "id": "sealed-bid-auction",
        "name": "Sealed-Bid Auction",
        "family": "Business and markets",
        "summary": "You bid once for an item you value at 60k, against a rival whose bid you cannot see. Winning cheaply is a victory; winning above your value is a failure; losing is a draw. Bidding too low or too high are both mistakes.",
        "initial": ("bid",),
        "terminal": terminal,
        "nature": nature,
        "nature_prompt": lambda s: "The rival's sealed bid is:",
        "prompt": lambda s: "Your sealed bid. What do you offer?",
        "options": lambda s: [("Bid 30k", ("rival", 30)), ("Bid 50k", ("rival", 50)), ("Bid 70k", ("rival", 70))],
    }


def main(out_path):
    sims = [build(d) for d in (salary(), tit_for_tat(), commons(), regime(), campaign(), cult_exit(), auction())]
    definitions = [salary(), tit_for_tat(), commons(), regime(), campaign(), cult_exit(), auction()]
    out = []
    for defn, built in zip(definitions, sims):
        entry = {k: defn[k] for k in ("id", "name", "family", "summary")}
        entry.update(built)
        out.append(entry)
    Path(out_path).write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", len(out), "simulations to", out_path)


if __name__ == "__main__":
    main(sys.argv[1])
