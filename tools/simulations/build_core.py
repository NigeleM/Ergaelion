"""Scored decision trees: author a simulation as rounds of options, each with a score and a reason.

A round offers options. An option may trigger a chance event with branches. Every
option and branch adds a score and carries a 'why' sentence, so the path can explain
itself. The final total decides the ending: victory, draw or failure.
"""


def O(label, score, why, chance=None):
    return {"label": label, "score": score, "why": why, "chance": chance}


def B(p, label, score, why):
    return (p, label, score, why)


def C(prompt, *branches):
    return (prompt, list(branches))


def R(prompt, *options):
    return {"prompt": prompt, "options": list(options)}


def S(sim_id, name, families, summary, rounds, win, draw, verdicts):
    return {
        "id": sim_id,
        "name": name,
        "families": families,
        "summary": summary,
        "rounds": rounds,
        "win": win,
        "draw": draw,
        "verdicts": verdicts,
    }


def build_scored(spec):
    """Build a scored tree. Every node is keyed by the path that reached it, so each ending
    records the exact choices behind it (the text names the path, not just the verdict)."""
    rounds = spec["rounds"]
    nodes, ids = {}, {}

    def name_of(key):
        if key not in ids:
            ids[key] = f"n{len(ids)}"
        return ids[key]

    def final_node(total, path):
        key = ("final", total, path)
        node = name_of(key)
        if node not in nodes:
            if total >= spec["win"]:
                outcome, text = "victory", spec["verdicts"][0]
            elif total >= spec["draw"]:
                outcome, text = "draw", spec["verdicts"][1]
            else:
                outcome, text = "failure", spec["verdicts"][2]
            trail = " -> ".join(path) if path else "no choices"
            nodes[node] = {"type": "end", "outcome": outcome,
                           "text": f"{text} Final score {total}. Path: {trail}."}
        return node

    def round_node(r, total, path):
        if r == len(rounds):
            return final_node(total, path)
        node = name_of(("round", r, total, path))
        if node in nodes:
            return node
        nodes[node] = None
        options = []
        for opt in rounds[r]["options"]:
            step = path + (opt["label"],)
            if opt["chance"]:
                prompt, branches = opt["chance"]
                after = total + opt["score"]
                chance_node = name_of(("chance", r, opt["label"], after, path))
                if chance_node not in nodes:
                    nodes[chance_node] = None
                    nodes[chance_node] = {
                        "type": "nature",
                        "prompt": prompt,
                        "branches": [
                            {"p": p, "label": label, "next": round_node(r + 1, after + score, step + (label,)), "why": why}
                            for p, label, score, why in branches
                        ],
                    }
                    assert abs(sum(p for p, _, _, _ in branches) - 1.0) < 1e-6, (spec["id"], opt["label"])
                options.append({"label": opt["label"], "next": chance_node, "why": opt["why"]})
            else:
                nxt = round_node(r + 1, total + opt["score"], step)
                options.append({"label": opt["label"], "next": nxt, "why": opt["why"]})
        nodes[node] = {"type": "player", "prompt": rounds[r]["prompt"], "options": options}
        return node

    start = round_node(0, 0, ())
    assert start == "n0"
    return {
        "id": spec["id"],
        "name": spec["name"],
        "families": spec["families"],
        "summary": spec["summary"],
        "start": start,
        "nodes": nodes,
    }
