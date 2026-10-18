"""Setup guides: how to describe your own situation for any game, from the game's own data.

The text comes from data/setup-help.json, so the guide for each game is generated from its
traits, options and payoff grid. Use `playbook setup <game>` for one game, `playbook setup --all`
for every game, and `--write FILE` to save a ready-to-edit scenario file.
"""

import json

from .catalog import DATA_DIR, TRAITS

HELP_FILE = DATA_DIR / "setup-help.json"


def load_help():
    """The shared setup text."""
    return json.loads(HELP_FILE.read_text(encoding="utf-8"))


def scenario_template(game):
    """A .gt scenario file prefilled with the game's traits and domains, for you to edit."""
    lines = [f"title: My {game['name']} situation"]
    for key in TRAITS:
        if key in game["traits"]:
            lines.append(f"{key}: {game['traits'][key]}")
    if game.get("domains"):
        lines.append(f"domain: {', '.join(game['domains'])}")
    lines.append("notes: Describe your situation here. Replace the example options with your own.")
    return "\n".join(lines) + "\n"


ENGLISH_LABELS = {
    "traits_heading": "## Traits and what each one means",
    "steps_heading": "## Steps to set up your own version",
    "options_heading": "## Options to model",
    "option_idea": "Option idea {n}: {rule}",
    "payoff_heading": "## Payoff grid",
    "payoff_rows": "Rows (you): {rows}. Columns (them): {cols}.",
    "payoff_enter": 'Enter it with: solve "{cells}" --rows {rows} --cols {cols}',
    "simulation_line": "Simulation: `sim {id}` shows the paths, and `sim {id} --play` lets you choose.",
    "template_heading": "## Start from this template",
}


def guide_text(game, help_data, sims_by_id):
    """The setup guide for one game as Markdown. Headings come from the help data's labels when present."""
    name, summary = game["name"], game["summary"]
    labels = dict(ENGLISH_LABELS, **help_data.get("labels", {}))
    lines = [f"# {name}", "", summary, "", labels["traits_heading"]]
    for key in TRAITS:
        if key in game["traits"]:
            value = game["traits"][key]
            lines.append(f"- {key} = {value}: {help_data['traits'][key][value]}")
    lines += ["", labels["steps_heading"]]
    lines += [f"{step}" for step in help_data["steps"]]
    lines += ["", labels["options_heading"]]
    for number, rule in enumerate(game["strategies"][:3], 1):
        lines.append("- " + labels["option_idea"].format(n=number, rule=rule))
    if game.get("matrix"):
        m = game["matrix"]
        cells = "; ".join(
            " ".join(f"{a},{b}" for a, b in row) for row in m["payoffs"]
        )
        rows, cols = ",".join(m["rows"]), ",".join(m["cols"])
        lines += [
            "",
            labels["payoff_heading"],
            labels["payoff_rows"].format(rows=", ".join(m["rows"]), cols=", ".join(m["cols"])),
            labels["payoff_enter"].format(cells=cells, rows=rows, cols=cols),
        ]
    if game["id"] in sims_by_id:
        lines += ["", labels["simulation_line"].format(id=game["id"])]
    lines += ["", labels["template_heading"], "```", scenario_template(game).rstrip(), "```"]
    return "\n".join(lines) + "\n"
