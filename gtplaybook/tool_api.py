"""Tool layer: the playbook's functions as tools other programs can call.

This module defines the tools a model could call, and routes each call to the playbook's own code.
It makes no network calls and needs no account, so the playbook works the same without it.

To use these tools from another program, send TOOLS with your request, and when the program asks
to use a tool, pass its name and input to call_tool(). The result is JSON, which goes back to the model as the tool
result. You can try any tool from the command line with:

    playbook tools                       list the tools and their input schemas
    playbook tool find_games '{"description": "price war"}'
"""

import json

from .catalog import DATA_DIR, find_game, load_areas, load_games
from .keywords import describe, suggest
from .repeat import DESCRIPTIONS, OPPONENTS, best_fixed_plan, check_rounds
from .sim import endings, load_simulations, solve

def _load_tools():
    """The tool schemas live in data/tools.json, so the Python and Go versions publish the same ones."""
    return json.loads((DATA_DIR / "tools.json").read_text(encoding="utf-8"))


TOOLS = _load_tools()


def _game_summary(game):
    out = {"id": game["id"], "name": game["name"], "category": game["category"], "summary": game["summary"],
           "how_it_works": game.get("how_it_works", ""), "strategies": game.get("strategies", []),
           "pitfalls": game.get("pitfalls", []), "examples": game.get("examples", [])}
    if game.get("matrix"):
        out["payoff_table"] = game["matrix"]
        out["payoff_table_note"] = game.get("matrix_note", "")
    elif game.get("matrix_unavailable"):
        out["payoff_table"] = None
        out["payoff_table_note"] = game["matrix_unavailable"]
    return out


def _tool_find_games(args, games):
    text = args["description"]
    result = suggest(text, games)
    return {
        "matched_phrases": result["phrases"],
        "games": [{"id": gid, "name": name, "matched": matched} for gid, name, matched in result["games"]],
        "areas": [family for family, _ in result["families"]],
        "simulations": [{"id": sid, "name": name} for sid, name in result["simulations"]],
        "message": describe(result, text),
    }


def _tool_get_game(args, games):
    return _game_summary(find_game(games, args["game"]))


def _tool_list_games(args, games):
    if args.get("area"):
        wanted = args["area"].lower()
        in_area = {gid for area in load_areas() if area["family"].lower() == wanted
                   for sub in area["subdomains"] for gid in sub["games"]}
        if not in_area:
            raise ValueError(f"no area named '{args['area']}'")
        games = [g for g in games if g["id"] in in_area]
    return [{"id": g["id"], "name": g["name"], "category": g["category"]} for g in games]


def _tool_solve_matrix(args, games):
    from .cli import solve_json
    from .solver import analyse, parse_matrix

    matrix = parse_matrix(args["matrix"])
    rows = [f"R{i + 1}" for i in range(len(matrix))]
    cols = [f"C{j + 1}" for j in range(len(matrix[0]))]
    analyse(matrix)  # raises on a malformed matrix
    return solve_json(matrix, rows, cols)


def _tool_list_simulations(args, games):
    sims = load_simulations()
    if args.get("mode"):
        sims = [s for s in sims if s.get("mode", "basic") == args["mode"]]
    return [{"id": s["id"], "name": s["name"], "mode": s.get("mode", "basic"), "families": s["families"]}
            for s in sims]


def _tool_get_simulation(args, games):
    from .sim import find_simulation

    sim = find_simulation(load_simulations(), args["simulation"])
    victory = solve(sim, "victory")[sim["start"]][0]
    failure = solve(sim, "failure")[sim["start"]][0]
    counts = {"victory": 0, "draw": 0, "failure": 0}
    for ending in endings(sim):
        counts[ending["outcome"]] += 1
    return {"id": sim["id"], "name": sim["name"], "mode": sim.get("mode", "basic"), "summary": sim["summary"],
            "chance_of_victory_on_best_path": _number(victory),
            "chance_of_failure_on_worst_path": _number(failure),
            "endings_found": counts}


def _tool_repeat_summary(args, games):
    game = find_game(games, args["game"])
    if not game.get("matrix"):
        raise ValueError(f"{game['name']} has no payoff table, so it cannot be repeated")
    rounds = check_rounds(args.get("rounds", 10))
    opponent = args["opponent"]
    row, total = best_fixed_plan(game["matrix"], rounds, opponent)
    return {"game": game["id"], "opponent": opponent, "rounds": rounds,
            "bot_rule": DESCRIPTIONS[opponent],
            "best_fixed_plan": {"row": game["matrix"]["rows"][row], "total": total}}


HANDLERS = {
    "find_games": _tool_find_games,
    "get_game": _tool_get_game,
    "list_games": _tool_list_games,
    "solve_matrix": _tool_solve_matrix,
    "list_simulations": _tool_list_simulations,
    "get_simulation": _tool_get_simulation,
    "repeat_summary": _tool_repeat_summary,
}


def call_tool(name, arguments, games=None):
    """Run one tool and return its result as JSON-ready data. Errors come back as {"error": ...}
    so the model can read them and try again, instead of the program stopping."""
    if name not in HANDLERS:
        return {"error": f"unknown tool '{name}'. Tools: {', '.join(HANDLERS)}"}
    if games is None:
        games = load_games()
    try:
        return HANDLERS[name](arguments or {}, games)
    except (ValueError, KeyError, TypeError) as exc:
        return {"error": str(exc)}


def tools_json():
    """The schemas exactly as data/tools.json holds them, so both versions print the same text."""
    return (DATA_DIR / "tools.json").read_text(encoding="utf-8")


def _number(value):
    """Whole numbers as integers, so the JSON matches the Go version."""
    value = float(value)
    return int(value) if value.is_integer() else round(value, 4)
