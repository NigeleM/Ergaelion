"""Export a finished simulation run to Markdown, JSON, CSV and the decision-tree SVG.

Each run is written to its own folder under the playbook home, named after the simulation and
the time, so runs never overwrite each other:

    <PLAYBOOK_HOME>/exports/<simulation-id>-<YYYYmmdd-HHMMSS>/
        run.md    the path you took and the ending, readable as a note
        run.json  the same run as data, for other tools
        run.csv   one row per step, for a spreadsheet
        tree.svg  the simulation's decision tree, with the best and worst paths coloured
"""

import csv
import datetime
import re
import io
import json
from pathlib import Path

from .catalog import playbook_home
from .charts import sim_tree
from .sim import endings, solve

FORMATS = ("md", "json", "csv", "svg")


def parse_formats(text):
    """Read a list such as 'md,csv' or 'all'. Returns the formats in their fixed order."""
    tokens = [token for token in text.replace(",", " ").lower().split() if token]
    if "all" in tokens:
        return list(FORMATS)
    unknown = [token for token in tokens if token not in FORMATS]
    if unknown:
        raise ValueError(f"unknown format(s): {', '.join(unknown)}. Use md, json, csv, svg or all.")
    return [fmt for fmt in FORMATS if fmt in tokens]


def run_record(sim, steps, ending):
    """The run as plain data: what was asked, what was chosen, and how it ended."""
    best = solve(sim, "victory")[sim["start"]][0]
    return {
        "simulation": sim["id"],
        "name": sim["name"],
        "families": sim["families"],
        "victory_chance_best_plan": round(best, 4),
        "ending": {"outcome": ending["outcome"], "text": ending["text"]},
        "steps": [
            {
                "kind": step["kind"],
                "prompt": step["prompt"],
                "choice": step["label"],
                "probability": step.get("p"),
                "why": step.get("why", ""),
            }
            for step in steps
        ],
    }


def run_markdown(sim, record):
    lines = [f"# {sim['name']}", "", f"*Works across: {', '.join(sim['families'])}*", "", sim["summary"], "",
             f"## Your run (best plan: {record['victory_chance_best_plan']:.0%} chance of victory)", ""]
    for number, step in enumerate(record["steps"], 1):
        if step["kind"] == "you":
            lines.append(f"{number}. {step['prompt']} **{step['choice']}**")
        else:
            lines.append(f"{number}. Chance: {step['choice']} ({step['probability']:.0%})")
        if step["why"]:
            lines.append(f"   - Why: {step['why']}")
    lines += ["", f"**Ending: {record['ending']['outcome'].upper()}.** {record['ending']['text']}", ""]
    return "\n".join(lines)


def run_csv(record):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["step", "kind", "prompt", "choice", "probability", "why"])
    for number, step in enumerate(record["steps"], 1):
        probability = "" if step["probability"] is None else step["probability"]
        writer.writerow([number, step["kind"], step["prompt"], step["choice"], probability, step["why"]])
    return buffer.getvalue()


def write_run(sim, steps, ending, formats, home=None, when=None):
    """Write the chosen formats for one run. Returns the folder and the files written."""
    home = Path(home) if home else playbook_home()
    stamp = (when or datetime.datetime.now()).strftime("%Y%m%d-%H%M%S")
    folder = home / "exports" / f"{sim['id']}-{stamp}"
    folder.mkdir(parents=True, exist_ok=True)
    record = run_record(sim, steps, ending)
    written = []
    for fmt in formats:
        path = folder / f"{'tree' if fmt == 'svg' else 'run'}.{fmt}"
        if fmt == "md":
            text = run_markdown(sim, record)
        elif fmt == "json":
            text = json.dumps(record, indent=2, ensure_ascii=False) + "\n"
        elif fmt == "csv":
            text = run_csv(record)
        else:
            text = sim_tree(sim, steps)
        path.write_text(text, encoding="utf-8")
        written.append(path)
    return folder, written


def ask_formats(prompt):
    """Offer the export choice after a run. Enter skips it."""
    print("\nExport this run? Type formats: md, json, csv, svg, or all. Press Enter to skip.")
    while True:
        answer = prompt("> ").strip()
        if not answer:
            return []
        try:
            return parse_formats(answer)
        except ValueError as error:
            print(f"  {error}")


def _stamp_folder(home, kind, name, when):
    stamp = (when or datetime.datetime.now()).strftime("%Y%m%d-%H%M%S")
    safe = re.sub(r"[^A-Za-z0-9_-]+", "-", name).strip("-") or "item"
    folder = Path(home) / "exports" / f"{kind}-{safe}-{stamp}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def game_markdown(game):
    """A game card as Markdown: what it is, its payoff table, how to play it, and the pitfalls."""
    lines = [f"# {game['name']}", "", f"*{game.get('category', '')}*", "", game["summary"], ""]
    if game.get("how_it_works"):
        lines += ["## How it works", "", game["how_it_works"], ""]
    if game.get("examples"):
        lines += ["## Scenarios it fits", ""] + [f"- {example}" for example in game["examples"]] + [""]
    matrix = game.get("matrix")
    if matrix:
        lines += ["## Reference payoff matrix", "", "Each cell is (your payoff, their payoff).", ""]
        lines.append("| | " + " | ".join(matrix["cols"]) + " |")
        lines.append("|---" * (len(matrix["cols"]) + 1) + "|")
        for label, row in zip(matrix["rows"], matrix["payoffs"]):
            lines.append(f"| {label} | " + " | ".join(f"({a}, {b})" for a, b in row) + " |")
        if game.get("matrix_note"):
            lines += ["", f"*{game['matrix_note']}*"]
        lines.append("")
    elif game.get("matrix_unavailable"):
        lines += ["## Payoff table", "", f"No table: {game['matrix_unavailable']}", ""]
    lines += ["## How to play it", ""]
    lines += [f"{number}. {rule}" for number, rule in enumerate(game.get("strategies", []), 1)] + [""]
    if game.get("pitfalls"):
        lines += ["## Pitfalls", ""] + [f"- {pitfall}" for pitfall in game["pitfalls"]] + [""]
    return "\n".join(lines)


def write_game(game, formats, home=None, when=None):
    """Export a game card. Games take md and json; the chart and CSV formats are for simulation runs."""
    unsupported = [fmt for fmt in formats if fmt not in ("md", "json")]
    if unsupported:
        raise ValueError(f"games export as md or json; {', '.join(unsupported)} is for simulation runs.")
    home = Path(home) if home else playbook_home()
    folder = _stamp_folder(home, "game", game["id"], when)
    written = []
    for fmt in formats:
        path = folder / f"game.{fmt}"
        if fmt == "md":
            path.write_text(game_markdown(game), encoding="utf-8")
        else:
            path.write_text(json.dumps(game, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(path)
    return folder, written


def write_repeat(game, opponent, rounds, seed, history, total, best, home=None, when=None):
    """Export a repeated-play run: each round, the totals, and the best fixed plan as a reference."""
    home = Path(home) if home else playbook_home()
    folder = _stamp_folder(home, "repeat", game["id"], when)
    matrix = game["matrix"]
    record = {
        "game": game["id"],
        "name": game["name"],
        "opponent": opponent,
        "rounds": rounds,
        "seed": seed,
        "your_total": total,
        "best_fixed_plan": {"row": matrix["rows"][best[0]], "total": best[1]},
        "rounds_played": [
            {"round": number, "your_choice": matrix["rows"][row], "bot_choice": matrix["cols"][col],
             "your_payoff": mine, "bot_payoff": theirs}
            for number, (row, col, mine, theirs) in enumerate(history, 1)
        ],
    }
    md = [f"# {game['name']}: repeated against a {opponent} bot", "",
          f"Rounds: {rounds}. Your total: {total}. Best always-the-same plan: always "
          f"{matrix['rows'][best[0]]}, total {best[1]}.", "", "| Round | You | Bot | You get | Bot gets |",
          "|---|---|---|---|---|"]
    md += [f"| {r['round']} | {r['your_choice']} | {r['bot_choice']} | {r['your_payoff']} | {r['bot_payoff']} |"
           for r in record["rounds_played"]]
    (folder / "run.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (folder / "run.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return folder, ["run.md", "run.json"]
