"""Simulations: decision trees you can play, or analyse for paths to victory and failure.

A simulation is a graph of nodes stored in data/simulations.json. Each node is one of:
  player  - you choose one of several options
  nature  - chance chooses a branch, with a probability for each
  end     - the outcome: victory, draw or failure

The engine can play a simulation interactively, find the plan with the best chance
of victory, find the plan that most often leads to failure, and list every ending.
To add or change a simulation, edit the JSON; the structure is described in the README.
"""

import json
import random
from pathlib import Path

from .catalog import DATA_DIR

SIM_FILE = "simulations.json"


def load_simulations(data_dir=DATA_DIR):
    sims = json.loads((Path(data_dir) / SIM_FILE).read_text(encoding="utf-8"))
    return [resolve_opponents(sim) for sim in sims]


def resolve_opponents(sim):
    """Turn each opponent step into a chance step whose odds depend on the choice you just made.

    An opponent step lists its replies and a policy: for each of your choices, named by its label,
    the chance of each reply. In a tree the step follows exactly one of your choices, so its odds are
    fixed and the solver treats it like chance. A choice with no policy entry uses the default odds.
    """
    nodes = sim["nodes"]
    came_from = {}
    for node in nodes.values():
        if node["type"] == "player":
            for option in node["options"]:
                came_from.setdefault(option["next"], option["label"])
        elif node["type"] == "nature":
            for branch in node["branches"]:
                came_from.setdefault(branch["next"], None)
    resolved = dict(nodes)
    for node_id, node in nodes.items():
        if node["type"] != "opponent":
            continue
        odds = node.get("policy", {}).get(came_from.get(node_id), node["default"])
        resolved[node_id] = {
            "type": "nature", "prompt": node["prompt"], "opponent": True,
            "branches": [{"p": p, "label": r["label"], "next": r["next"], "why": r.get("why", "")}
                         for p, r in zip(odds, node["replies"])],
        }
    return {**sim, "nodes": resolved}


def find_simulation(sims, query):
    needle = query.lower().strip()
    exact = [s for s in sims if s["id"] == needle or s["name"].lower() == needle]
    if exact:
        return exact[0]
    partial = [s for s in sims if needle in s["id"] or needle in s["name"].lower()]
    if len(partial) == 1:
        return partial[0]
    if not partial:
        raise ValueError(f"no simulation matches '{query}'")
    raise ValueError(f"'{query}' is ambiguous: " + ", ".join(s["id"] for s in partial))


def solve(sim, goal="victory"):
    """Return {node_id: (chance_of_goal, chosen_option_index)} for the plan that maximises goal.

    goal is 'victory' for the path to victory, or 'failure' for the path most likely to fail.
    """
    nodes = sim["nodes"]
    memo = {}

    def value(nid):
        if nid in memo:
            return memo[nid][0]
        node = nodes[nid]
        if node["type"] == "end":
            memo[nid] = (1.0 if node["outcome"] == goal else 0.0, None)
        elif node["type"] == "nature":
            total = sum(b["p"] * value(b["next"]) for b in node["branches"])
            memo[nid] = (total, None)
        else:
            scores = [value(o["next"]) for o in node["options"]]
            index = max(range(len(scores)), key=lambda i: scores[i])
            memo[nid] = (scores[index], index)
        return memo[nid][0]

    value(sim["start"])
    return memo


def trace(sim, plan):
    """Follow a plan from the start. Chance is resolved by the likeliest branch.

    Returns (steps, ending_node, chance_of_victory_under_the_plan).
    """
    nodes = sim["nodes"]
    nid = sim["start"]
    steps = []
    while True:
        node = nodes[nid]
        if node["type"] == "end":
            return steps, node, plan[sim["start"]][0]
        if node["type"] == "nature":
            branch = max(node["branches"], key=lambda b: b["p"])
            steps.append({"kind": "chance", "prompt": node["prompt"], "label": branch["label"],
                          "p": branch["p"], "why": branch.get("why", "")})
            nid = branch["next"]
        else:
            index = plan[nid][1]
            option = node["options"][index]
            steps.append({"kind": "you", "prompt": node["prompt"], "label": option["label"],
                          "why": option.get("why", "")})
            nid = option["next"]


def endings(sim, limit=2000):
    """Enumerate every reachable ending with its probability and the choices that reach it."""
    nodes = sim["nodes"]
    results = []

    def walk(nid, steps, prob):
        if len(results) >= limit:
            return
        node = nodes[nid]
        if node["type"] == "end":
            results.append({"steps": steps, "prob": prob, "outcome": node["outcome"], "text": node["text"]})
        elif node["type"] == "nature":
            for b in node["branches"]:
                step = {"kind": "chance", "prompt": node["prompt"], "label": b["label"], "p": b["p"],
                        "why": b.get("why", "")}
                walk(b["next"], steps + [step], prob * b["p"])
        else:
            for o in node["options"]:
                step = {"kind": "you", "prompt": node["prompt"], "label": o["label"],
                        "why": o.get("why", "")}
                walk(o["next"], steps + [step], prob)

    walk(sim["start"], [], 1.0)
    return results


def play(sim, ask, say, rng=None, node=None, steps=None, checkpoint=None):
    """Play one run interactively.

    ask(prompt, options) returns the 0-based index of the chosen option. Each option is a dict
    with 'label', 'why' and 'chance' (the chance of victory from there under the best plan),
    so the player can see why the other choices were not taken.
    say(text) shows a line of narration, such as a chance result.
    Returns (steps, ending_node).
    """
    rng = rng or random.Random()
    nodes = sim["nodes"]
    values = solve(sim, "victory")
    nid = node or sim["start"]
    steps = list(steps or [])
    history = []  # (decision node, steps before it) for walking back
    while True:
        node = nodes[nid]
        if checkpoint:
            checkpoint(nid, steps)
        if node["type"] == "end":
            return steps, node
        if node["type"] == "nature":
            roll, cumulative = rng.random(), 0.0
            branch = node["branches"][-1]
            for b in node["branches"]:
                cumulative += b["p"]
                if roll < cumulative:
                    branch = b
                    break
            say(f"{node['prompt']} {branch['label']}")
            steps.append({"kind": "chance", "prompt": node["prompt"], "label": branch["label"],
                          "p": branch["p"], "why": branch.get("why", "")})
            nid = branch["next"]
        else:
            options = [{"label": o["label"], "why": o.get("why", ""), "chance": values[o["next"]][0]}
                       for o in node["options"]]
            index = ask(node["prompt"], options)
            if index is None:  # walk back to the previous decision and take it again
                if history:
                    nid, steps = history.pop()
                    steps = list(steps)
                continue
            chosen = node["options"][index]
            history.append((nid, list(steps)))
            steps.append({"kind": "you", "prompt": node["prompt"], "label": chosen["label"],
                          "why": chosen.get("why", "")})
            nid = chosen["next"]


def save_state(path, sim, node_id, steps):
    """Write a saved game to a JSON file, so it can be resumed later."""
    data = {"simulation": sim["id"], "node": node_id, "steps": steps}
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_state(path, sim):
    """Read a saved game. Raises ValueError if it belongs to another simulation or is unusable."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("simulation") != sim["id"]:
        raise ValueError(f"that save is for '{data.get('simulation')}', not '{sim['id']}'")
    if data.get("node") not in sim["nodes"]:
        raise ValueError("that save refers to a step this simulation does not have")
    return data["node"], data["steps"]
