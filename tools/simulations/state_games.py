"""Full-rules games: generate the whole decision tree from the rules of a game.

A game is described by functions over hashable states:
  player(state)   -> [(label, why, next_state)] your legal moves
  opponent(state) -> [(p, label, why, next_state)] the opponent's replies, with probabilities
  result(state)   -> None while play continues, or (outcome, text) when the game is over
  prompt(state), opp_prompt(state) -> the questions shown to the player

Each state becomes one node, so two paths that reach the same position share it. The result is
a tree of player, nature and end nodes that the same engine plays and solves as every other
simulation. The opponent is modelled as chance: a uniform random reply, or a fixed reply
with probability 1.0 for a deterministic opponent.
"""


def build_state_game(spec):
    nodes, ids = {}, {}

    def name_of(key):
        if key not in ids:
            ids[key] = f"n{len(ids)}"
        return ids[key]

    def end_node(outcome, text):
        node = name_of(("end", outcome, text))
        nodes.setdefault(node, {"type": "end", "outcome": outcome, "text": text})
        return node

    def check(state):
        found = spec["result"](state)
        return end_node(*found) if found else None

    def player_node(state):
        node = name_of(("P", state))
        if node in nodes:
            return node
        nodes[node] = None
        options = []
        for label, why, nxt in spec["player"](state):
            target = check(nxt) or opponent_node(nxt)
            options.append({"label": label, "next": target, "why": why})
        nodes[node] = {"type": "player", "prompt": spec["prompt"](state), "options": options}
        return node

    def opponent_node(state):
        node = name_of(("O", state))
        if node in nodes:
            return node
        nodes[node] = None
        replies = spec["opponent"](state)
        assert replies, ("no opponent reply in a game that is not over", state)
        branches = []
        for p, label, why, nxt in replies:
            target = check(nxt) or player_node(nxt)
            branches.append({"p": p, "label": label, "next": target, "why": why})
        assert abs(sum(b["p"] for b in branches) - 1.0) < 1e-9, ("probabilities must sum to 1", state)
        nodes[node] = {"type": "nature", "prompt": spec["opp_prompt"](state), "branches": branches}
        return node

    start = spec["start"]
    first = check(start) or player_node(start)
    assert first == "n0"
    return {
        "id": spec["id"],
        "name": spec["name"],
        "families": spec["families"],
        "summary": spec["summary"],
        "start": first,
        "mode": "live",
        "nodes": nodes,
    }
