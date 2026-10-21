"""Command-line interface for the Game Theory Playbook.

With no arguments it opens the interactive session (see repl.py). The same
commands are available as subcommands for scripting:

    playbook list --domain military
    playbook show chicken
    playbook advise examples/salary-negotiation.gt
    playbook advise -d "two companies set prices at the same time, once only"
    playbook solve "3,3 0,5; 5,0 1,1" --rows Cooperate,Defect --cols Cooperate,Defect
    playbook new my-situation.gt
    playbook template
"""

import argparse
import sys
import textwrap
from pathlib import Path

from . import advisor, solver
import copy
import json

from . import record
from .catalog import DATA_DIR, NON_GAME_FILES, TRAITS, check_overlays, find_game, load_areas, load_games, load_topics, playbook_home, save_overlay, set_disabled
from .scenario import DOMAIN_WORDS, TEMPLATE, describe, normalise, parse_scenario
from . import keywords
from .i18n import t
from .exporter import ask_formats, parse_formats, write_game, write_repeat, write_run
from .engine import engine_games, find_engine_game
from .engine import play as play_engine
from .matrix_sim import matrix_simulation
from .repeat import DESCRIPTIONS, MAX_ROUNDS, OPPONENTS, best_fixed_plan, check_rounds, outcome_for_log, play_repeated
from .setup_guide import guide_text, load_help, scenario_template
from .sim import load_state, save_state
from .sim import endings, find_simulation, load_simulations, play, solve, trace
from .ui import ROLES, THEMES, accent, bad, bold, box, cell, dim, good, green, heading, load_theme, mid, plain, red, parse_colour, reset_theme, save_theme, current_theme

WIDTH = 88
VERSION = "1.0.0"


# ---- text layout -------------------------------------------------------------

def wrap_text(text, first, rest, marker=""):
    return textwrap.fill(
        f"{marker} {text}" if marker else text,
        WIDTH,
        initial_indent=first,
        subsequent_indent=rest,
        break_on_hyphens=False,
    )


def paragraph(text):
    return wrap_text(text, "  ", "  ")


def bullet(text, marker="•", indent=2):
    pad = " " * indent
    return wrap_text(text, pad, pad + " " * (len(marker) + 1), marker=marker)


def format_traits(traits):
    return ", ".join(f"{key}={traits[key]}" for key in TRAITS if key in traits)


def prompt(message):
    try:
        return input(message)
    except EOFError:
        print()
        sys.exit(0)


def new_scenario():
    return {"title": "", "notes": "", "domains": [], "traits": {}}


# ---- shared pieces: grids, scenarios, advice --------------------------------

def print_grid(rows, cols, payoffs, equilibria=(), dropped_rows=(), dropped_cols=()):
    """The payoff grid. Pure equilibria are green; strategies removed by dominance are dimmed."""
    label_w = max(len(name) for name in rows) + 2
    col_w = max(max(len(name) for name in cols) + 2, 12)
    headers = "".join(cell(name, col_w, dim if j in dropped_cols else bold) for j, name in enumerate(cols))
    print(" " * label_w + headers)
    for i, (name, row) in enumerate(zip(rows, payoffs)):
        cells = ""
        for j, (a, b) in enumerate(row):
            if (i, j) in equilibria:
                styler = good
            elif i in dropped_rows or j in dropped_cols:
                styler = dim
            else:
                styler = plain
            cells += cell(f"({a}, {b})", col_w, styler)
        print(cell(name, label_w, dim if i in dropped_rows else bold) + cells)
    print(dim("  " + t("each_cell")))
    if equilibria or dropped_rows or dropped_cols:
        print(dim("  " + t("grid_key")))


def action_names(text, count, prefix):
    if not text:
        return [f"{prefix}{i + 1}" for i in range(count)]
    names = [name.strip() for name in text.split(",")]
    if len(names) != count:
        raise ValueError(f"expected {count} action names, got {len(names)}")
    return names


def scenario_from_args(file=None, describe_text=None):
    if file:
        return parse_scenario(Path(file).read_text(encoding="utf-8"))
    if describe_text:
        sc = describe(describe_text)
        show_inferred(sc)
        return sc
    return new_scenario()


def apply_sets(sc, items):
    for item in items:
        key, sep, value = item.partition("=")
        if not sep:
            raise ValueError(f"expected KEY=VALUE, got '{item}'")
        key = key.strip().lower()
        sc["traits"][key] = normalise(key, value)


def show_inferred(sc):
    print("\n" + heading(t("reading")))
    if not sc["traits"] and not sc["domains"]:
        print(bullet("nothing recognised"))
    for key in TRAITS:
        if key in sc["traits"]:
            matched = dim(f"(matched '{sc['evidence'][key]}')")
            print(bullet(f"{key} = {sc['traits'][key]}  {matched}"))
    for domain in sc["domains"]:
        print(bullet(f"domain = {domain}"))
    print(dim("Override any trait with /set key=value."))


def corrected_text(text, games):
    """The description with clear typos fixed, for matching. Returns (text, corrections)."""
    if not text:
        return text, []
    vocabulary = keywords.vocabulary(games, combinations=advisor.load_combinations())
    return keywords.correct_text(text, vocabulary)


def suggest_spelling(text, games):
    """When nothing matches, point out words that may be typos and offer the nearest known words."""
    if not text:
        return
    vocabulary = keywords.vocabulary(games, combinations=advisor.load_combinations())
    close = keywords.close_words(text, vocabulary)
    if close:
        print(dim("Did you mean: " + "; ".join(f"{word} → {', '.join(options)}" for word, options in close)))


def print_combined(sc, games, hits):
    """Blended advice: strategies from several games, multi-game playbooks for complex situations, and
    scenarios to play. Shown for plain-English descriptions, where one game may not fit the whole situation."""
    text = sc.get("text", "")
    if not text:
        return
    combos = advisor.matched_combinations(text, advisor.load_combinations())
    if len(hits) >= 2 and hits[1]["score"] >= 1:
        print("\n" + heading("Combined advice"))
        print(dim("No single game covers all of this, so these come from the best fits together."))
        for game_name, strategy in advisor.combined_rules(hits):
            print(bullet(f"{strategy}  ({game_name})"))
    for item in combos:
        combo = item["combination"]
        print("\n" + heading(combo["name"]))
        print(dim("matched: " + ", ".join(item["phrases"])))
        print(paragraph(combo["combined"]))
        print(dim("Games that combine here: " + ", ".join(combo["games"])))
        for step in combo["steps"]:
            print(bullet(step, marker="•"))
        for warn in combo["watch_outs"]:
            print(dim(bullet("watch out: " + warn, marker="!")))
    suggestion = keywords.suggest(text, games)
    if suggestion["simulations"]:
        print("\n" + heading("Scenarios to play"))
        for sim_id, name in suggestion["simulations"][:3]:
            print(bullet(f"{name}  {dim(sim_id)}"))


def print_advice(sc, games, top):
    if not sc["traits"] and not sc["domains"] and not sc.get("text"):
        raise ValueError(t("no_traits"))
    text, corrections = corrected_text(sc.get("text", ""), games)
    hits = advisor.rank_games(games, sc["traits"], sc["domains"], top=top, records=record.tally(),
                              text=text, keyword_data=keywords.load_keywords())
    if not sc["traits"] and not sc["domains"] and (not hits or hits[0]["score"] == 0):
        if not advisor.matched_combinations(text, advisor.load_combinations()):
            for line in keywords.describe(keywords.suggest(text, games), text):
                print(line)
            return
        print_combined(dict(sc, text=text), games, [])
        return
    sc = dict(sc, text=text)
    print("\n" + bold(sc["title"] or "Scenario"))
    if sc["traits"]:
        print(dim(format_traits(sc["traits"])))
    if sc["domains"]:
        print(dim("domains: " + ", ".join(sc["domains"])))
    if not sc["traits"] and sc["domains"]:
        print(dim("Only the domain matched. Add traits with /set for sharper advice."))
    if corrections:
        print(dim("Reading your words as: " + text))
    print("\n" + heading(t("best_fit")))
    for number, hit in enumerate(hits, 1):
        game = hit["game"]
        fit = dim(f"fit {hit['score']:+.1f}")
        print(f"\n{bold(str(number) + '.')} {bold(game['name'])}  {fit}")
        if hit["phrases"]:
            print(green(bullet("phrases: " + ", ".join(hit["phrases"]), marker="+")))
        if hit["words"]:
            print(green(bullet("shared words: " + ", ".join(hit["words"]), marker="+")))
        if hit["matched"]:
            print(green(bullet("agrees on: " + ", ".join(hit["matched"]), marker="+")))
        if hit["clashed"]:
            print(red(bullet("differs on: " + ", ".join(hit["clashed"]), marker="−")))
        line = record_line(game["id"])
        if line:
            nudge = hit["record_adjustment"]
            effect = f", your results adjust the fit by {nudge:+.1f}" if nudge else ""
            print(dim(f"{t('your_record')}: {line}{effect}"))
        print(dim(paragraph(game["summary"])))
    if not hits or hits[0]["score"] < 1:
        print("\n" + red(t("weak_match")))
        suggest_spelling(sc.get("text", ""), games)
    print_combined(sc, games, hits)

    print("\n" + heading(t("rules_here")))
    for rule in advisor.general_rules(sc["traits"]):
        print(bullet(rule))
    if hits:
        best = hits[0]["game"]
        print("\n" + heading(t("playbook_for", name=best["name"])))
        for number, step in enumerate(best["strategies"], 1):
            print(bullet(step, marker=f"{number}."))


def recommendation(result, rows, cols):
    if len(result["surviving_rows"]) == 1 and len(result["surviving_cols"]) == 1:
        return (f"Dominance settles it: play {rows[result['surviving_rows'][0]]}. "
                f"Expect them to play {cols[result['surviving_cols'][0]]}.")
    if len(result["equilibria"]) == 1:
        return "Play your part of the equilibrium. It holds if they also reason to it."
    if len(result["equilibria"]) > 1:
        return ("Several pure equilibria: pick the one you prefer and agree it in advance, "
                "because uncoordinated play can land on a bad outcome.")
    if result["mixed"]:
        return "No pure equilibrium: randomise with the mixed probabilities above so they cannot predict or exploit you."
    _, indices = result["row_maximin"]
    value, _ = result["row_maximin"]
    return f"No equilibrium here: play maximin ({', '.join(rows[i] for i in indices)}) to guarantee at least {value}."


def dominance_reason(matrix, rows, cols, player, index):
    """Why a strategy is strictly dominated, using the whole grid. None when only the steps above show it."""
    if player == "row":
        for k in range(len(rows)):
            if k != index and all(matrix[k][j][0] > matrix[index][j][0] for j in range(len(cols))):
                cases = " ".join(f"If they play {cols[j]}, {rows[k]} gives you {matrix[k][j][0]} and "
                                 f"{rows[index]} gives you {matrix[index][j][0]}." for j in range(len(cols)))
                return f"{rows[index]} is strictly dominated by {rows[k]}: whatever they play, {rows[k]} pays you more. {cases}"
    else:
        for k in range(len(cols)):
            if k != index and all(matrix[i][k][1] > matrix[i][index][1] for i in range(len(rows))):
                cases = " ".join(f"If you play {rows[i]}, {cols[k]} gives them {matrix[i][k][1]} and "
                                 f"{cols[index]} gives them {matrix[i][index][1]}." for i in range(len(rows)))
                return f"{cols[index]} is strictly dominated by {cols[k]}: whatever you play, {cols[k]} pays them more. {cases}"
    return None


def print_solution(result, rows, cols, matrix):
    print("\n" + heading(t("analysis")))
    for player, index in result["eliminated"]:
        name, owner = (rows[index], "you") if player == "row" else (cols[index], "them")
        print(bullet(f"strictly dominated, can be dropped: {name} ({owner})"))
        reason = dominance_reason(matrix, rows, cols, player, index)
        if reason:
            print(dim(paragraph(reason)))
    surviving_rows = [rows[i] for i in result["surviving_rows"]]
    surviving_cols = [cols[j] for j in result["surviving_cols"]]
    print(bullet(f"after dominance: you {', '.join(surviving_rows)}, them {', '.join(surviving_cols)}"))

    if result["equilibria"]:
        for i, j in result["equilibria"]:
            a, b = matrix[i][j]
            print(green(bullet(f"pure equilibrium: you {rows[i]}, them {cols[j]}  payoffs ({a}, {b})")))
    else:
        print(bullet("no pure-strategy equilibrium"))

    if result["mixed"]:
        p, q = result["mixed"]
        print(bullet(
            f"mixed equilibrium: you play {rows[0]} {float(p):.1%}, {rows[1]} {float(1 - p):.1%}; "
            f"they play {cols[0]} {float(q):.1%}, {cols[1]} {float(1 - q):.1%}"
        ))

    value, indices = result["row_maximin"]
    print(bullet(f"your maximin (safe) value: {value}, achieved by {', '.join(rows[i] for i in indices)}"))
    value, indices = result["col_maximin"]
    print(bullet(f"their maximin (safe) value: {value}, achieved by {', '.join(cols[j] for j in indices)}"))
    if result["constant_sum"] is not None:
        print(bullet(f"constant-sum game: totals are always {result['constant_sum']}, "
                     "so one side's gain is the other's loss"))

    print("\n" + heading(t("recommendation")))
    lines = textwrap.wrap(recommendation(result, rows, cols), 70)
    print(box(lines, border=accent))


# ---- subcommands -------------------------------------------------------------

def cmd_list(args, games):
    selected = games
    if args.domain:
        selected = [g for g in selected if args.domain in g["domains"]]
    if args.search:
        needle = args.search.lower()
        selected = [g for g in selected if needle in repr(g).lower()]
    id_width = max((len(g["id"]) for g in selected), default=0) + 2
    name_width = max((len(g["name"]) for g in selected), default=0) + 2
    for game in selected:
        print(cell(game["id"], id_width, bold) + cell(game["name"], name_width) + dim(game["category"]))
    print()
    print(dim(f"{len(selected)} game(s). Run 'show <id>' for its playbook."))
    return 0


def matrix_note_for(game):
    return game.get("matrix_note", "")


def cmd_show(args, games):
    game = find_game(games, args.game)
    name, summary = game["name"], game["summary"]
    print(f"\n{bold(name)}  {dim('[' + game['category'] + ']')}\n")
    print(paragraph(summary))
    print("\n" + heading(t("how_it_works")))
    print(paragraph(game["how_it_works"]))
    print("\n" + dim("Traits: " + format_traits(game["traits"])))
    print(dim("Domains: " + ", ".join(game["domains"])))
    if game.get("examples"):
        print("\n" + heading(t("scenarios_fit")))
        for example in game["examples"]:
            print(bullet(example))
    if game.get("matrix"):
        print("\n" + heading(t("reference_matrix")))
        matrix = game["matrix"]
        print_grid(matrix["rows"], matrix["cols"], matrix["payoffs"])
        if matrix_note_for(game):
            print(dim(paragraph(matrix_note_for(game))))
    elif game.get("matrix_unavailable"):
        print("\n" + heading("Payoff table"))
        print(dim(paragraph("No table: " + game["matrix_unavailable"])))
    print("\n" + heading(t("how_to_play")))
    for number, rule in enumerate(game["strategies"], 1):
        print(bullet(rule, marker=f"{number}."))
    if game.get("pitfalls"):
        print("\n" + heading(t("pitfalls")))
        for pitfall in game["pitfalls"]:
            print(bullet(pitfall))
    if game.get("sources"):
        print("\n" + heading(t("sources")))
        for source in game["sources"]:
            print(bullet(source))
    print("\n" + dim(t("verify_note")))
    formats = getattr(args, "formats", None)
    if formats:
        folder, written = write_game(game, parse_formats(formats))
        print(dim(f"Exported to {folder}: " + ", ".join(path.name for path in written)))
    return 0


def cmd_advise(args, games):
    sc = scenario_from_args(file=args.file, describe_text=args.describe)
    apply_sets(sc, args.set or [])
    print_advice(sc, games, args.top)
    return 0


def cmd_tools(args, games):
    from .tool_api import tools_json

    print(tools_json(), end="")
    return 0


def cmd_tool(args, games):
    import json as _json

    from .tool_api import call_tool

    try:
        arguments = _json.loads(args.arguments)
    except ValueError as exc:
        raise ValueError(f"the arguments must be JSON: {exc}")
    print(_json.dumps(call_tool(args.name, arguments, games), indent=2, ensure_ascii=False, sort_keys=True))
    return 0


def cmd_help(args, games):
    from .catalog import DATA_DIR

    print((DATA_DIR / "help.txt").read_text(encoding="utf-8"), end="")
    return 0


def cmd_version(args, games):
    print("playbook 1.0.0")
    return 0


def cmd_keywords(args, games):
    from . import keywords

    text = " ".join(args.words)
    print()
    for line in keywords.describe(keywords.suggest(text, games), text):
        print(line)
    return 0


def _number(value):
    """A whole number is written as an integer, so the JSON matches the Go version."""
    value = float(value)
    return int(value) if value.is_integer() else value


def solve_json(matrix, rows, cols):
    """The solution as data: the dominance steps, surviving strategies, maximin values and equilibria."""
    result = solver.analyse(matrix)
    equilibria = solver.support_equilibria(matrix) if len(matrix) <= 4 and len(matrix[0]) <= 4 else None
    return {
        "rows": rows,
        "cols": cols,
        "matrix": [[[_number(a), _number(b)] for a, b in row] for row in matrix],
        "eliminated": [{"player": "row" if kind == "row" else "col",
                        "strategy": rows[i] if kind == "row" else cols[i]} for kind, i in result["eliminated"]],
        "surviving_rows": [rows[i] for i in result["surviving_rows"]],
        "surviving_cols": [cols[j] for j in result["surviving_cols"]],
        "maximin_row": {"value": _number(result["row_maximin"][0]),
                        "strategies": [rows[i] for i in result["row_maximin"][1]]},
        "maximin_col": {"value": _number(result["col_maximin"][0]),
                        "strategies": [cols[j] for j in result["col_maximin"][1]]},
        "equilibria": None if equilibria is None else [
            {"you": {rows[i]: _number(x) for i, x in enumerate(row_mix) if x},
             "them": {cols[j]: _number(x) for j, x in enumerate(col_mix) if x}}
            for row_mix, col_mix in equilibria],
    }


def cmd_solve(args, games):
    matrix = solver.parse_matrix(args.matrix)
    rows = action_names(args.rows, len(matrix), "R")
    cols = action_names(args.cols, len(matrix[0]), "C")
    if args.json:
        print(json.dumps(solve_json(matrix, rows, cols), indent=2, ensure_ascii=False, sort_keys=True))
        return 0
    result = solver.analyse(matrix)
    print("\n" + heading(t("payoff_matrix")))
    print_grid(rows, cols, [[(str(a), str(b)) for a, b in row] for row in matrix],
               equilibria=set(map(tuple, result["equilibria"])),
               dropped_rows={i for player, i in result["eliminated"] if player == "row"},
               dropped_cols={j for player, j in result["eliminated"] if player == "col"})
    print_solution(result, rows, cols, matrix)
    if len(matrix) <= 4 and len(matrix[0]) <= 4:
        equilibria = solver.support_equilibria(matrix)
        print("\n" + heading(t("every_equilibrium")))
        for number, (row_mix, col_mix) in enumerate(equilibria, 1):
            you = ", ".join(f"{rows[i]} {float(x):.1%}" for i, x in enumerate(row_mix) if x)
            them = ", ".join(f"{cols[j]} {float(x):.1%}" for j, x in enumerate(col_mix) if x)
            print(bullet(f"equilibrium {number}: you {you}; them {them}"))
        if not equilibria:
            print(bullet("none found"))
    return 0


def ask_choice(key, options):
    listing = " / ".join(f"{number}) {option}" for number, option in enumerate(options, 1))
    answer = prompt(f"{key}: {listing}  [Enter to skip] ").strip().lower()
    if not answer:
        return None
    if answer.isdigit() and 1 <= int(answer) <= len(options):
        return options[int(answer) - 1]
    if answer in options:
        return answer
    print(red("  not recognised, skipping"))
    return None


def cmd_new(args, games):
    path = Path(args.path)
    if path.exists() and prompt(f"{path} exists. Overwrite? [y/N] ").strip().lower() != "y":
        print("Cancelled.")
        return 1
    title = prompt("Title for this situation: ").strip()
    domains = prompt(f"Domains, comma separated ({', '.join(DOMAIN_WORDS)}), Enter to skip: ").strip()
    print("\n" + dim("For each question, type a number, or press Enter to skip that trait."))

    lines = [f"title: {title}"] if title else []
    for key, options in TRAITS.items():
        choice = ask_choice(key, options)
        if choice:
            lines.append(f"{key}: {choice}")
    if domains:
        lines.append(f"domain: {domains}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(green(f"Saved {path}"))
    if prompt("Advise on it now? [Y/n] ").strip().lower() != "n":
        return cmd_advise(argparse.Namespace(file=str(path), describe=None, set=None, top=3), games)
    return 0


def cmd_template(args, games):
    print(TEMPLATE)
    return 0


def record_line(game_id):
    counts = record.tally().get(game_id)
    if not counts or not sum(counts.values()):
        return None
    return record.format_record(counts)


def topic_games(games, topic_id):
    """The games that belong to a topic, by name."""
    return sorted((game for game in games if topic_id in game["domains"]), key=lambda game: game["name"])


def game_locations():
    """Each game's family and sub-domain, for showing where a game sits in the families."""
    places = {}
    for family in load_areas():
        for sub in family["subdomains"]:
            for game_id in sub["games"]:
                places.setdefault(game_id, f"{family['family']}: {sub['name']}")
    return places


def cmd_topics(args, games):
    topics = load_topics()
    name = " ".join(args.name).lower()
    if not name:
        print()
        for topic in topics:
            count = len(topic_games(games, topic["id"]))
            print(bold(topic["name"]) + "  " + dim(f"{count} games"))
            print(dim(paragraph(topic["summary"])))
        print(dim("\nRun 'topics <topic>' for its games, e.g. 'topics military'."))
        return 0
    exact = [item for item in topics if name in (item["id"], item["name"].lower())]
    partial = [item for item in topics if name in item["id"] or name in item["name"].lower()]
    matches = exact or partial
    if not matches:
        raise ValueError(f"no topic matches '{name}'. Run 'topics' to list them.")
    if len(matches) > 1:
        raise ValueError(f"'{name}' is ambiguous: " + ", ".join(item["name"] for item in matches))
    topic = matches[0]
    places = game_locations()
    print("\n" + bold(topic["name"]))
    print(dim(paragraph(topic["summary"])))
    print()
    for game in topic_games(games, topic["id"]):
        print(bullet(f"{game['name']}  {dim(places.get(game['id'], game['id']))}"))
    print(dim("\nRun 'show <game>' for any of them, or 'topics' for the other topics."))
    return 0


def cmd_areas(args, games):
    families = load_areas()
    name = " ".join(args.name).lower()
    if not name:
        print()
        for family in families:
            count = len({g for sd in family["subdomains"] for g in sd["games"]})
            print(bold(family["family"]) + "  " + dim(f"{count} games"))
            print(dim(paragraph(family["summary"])))
        print(dim("\nRun 'areas <family>' for its sub-domains and what to read, e.g. 'areas war'."))
        return 0
    exact = [f for f in families if f["family"].lower() == name]
    partial = [f for f in families if name in f["family"].lower()]
    matches = exact or partial
    if not matches:
        raise ValueError(f"no family matches '{name}'. Run 'areas' to list them.")
    if len(matches) > 1:
        raise ValueError(f"'{name}' is ambiguous: " + ", ".join(f["family"] for f in matches))
    family = matches[0]
    names = {g["id"]: g["name"] for g in games}
    print("\n" + bold(family["family"]))
    print(dim(paragraph(family["summary"])))
    for sd in family["subdomains"]:
        print("\n" + heading(sd["name"]))
        for game_id in sd["games"]:
            print(bullet(f"{names.get(game_id, game_id)}  {dim(game_id)}"))
    print("\n" + heading(t("learn_more")))
    for ref in family["learn"]:
        print(bullet(ref))
    return 0


def _ask_line(prompt):
    """A line from the player, or None at the end of input."""
    try:
        return input(prompt)
    except EOFError:
        return None


def cmd_engine(args, games):
    available = engine_games()
    if not args.name:
        print()
        for game in available:
            print(cell(game["id"], 22, bold) + cell(game["name"], 46) + dim(game["summary"]))
        print(dim("\nRun 'engine <id>' to play one, e.g. 'engine nim'."))
        return 0
    game = find_engine_game(available, " ".join(args.name))
    play_engine(game, ask=_ask_line, say=print, catalog=games)
    return 0


def cmd_log(args, games):
    game = find_game(games, args.game)
    if args.play is not None:
        if not 1 <= args.play <= len(game["strategies"]):
            raise ValueError(f"'{game['name']}' has plays 1 to {len(game['strategies'])}")
    record.log_outcome(game["id"], args.result, " ".join(args.note), play=args.play)
    where = f" with play {args.play}" if args.play is not None else ""
    print(green(f"Logged {args.result} for {game['name']}{where}. Record: {record_line(game['id'])}."))
    return 0


def cmd_record(args, games):
    if args.json:
        if args.game:
            game = find_game(games, args.game)
            data = {"game": game["id"], "entries": record.history(game["id"]), "tally": record.tally().get(game["id"], {})}
        else:
            data = {"tally": record.tally()}
        print(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True))
        return 0
    if args.csv:
        Path(args.csv).write_text(record.to_csv(), encoding="utf-8")
        print(green(f"Wrote your results to {args.csv}"))
        return 0
    if args.game:
        game = find_game(games, args.game)
        entries = record.history(game["id"])
        print("\n" + bold(game["name"]) + "  " + dim(record_line(game["id"]) or "no outcomes yet"))
        for entry in entries:
            note = f"  {entry['note']}" if entry["note"] else ""
            play = f"  play {entry['play']}" if entry.get("play") else ""
            print(bullet(f"{entry['date']}  {entry['result']}{play}{note}"))
        by_play = {}
        for entry in entries:
            if entry.get("play"):
                by_play.setdefault(entry["play"], {r: 0 for r in record.RESULTS})[entry["result"]] += 1
        if by_play:
            print("\n" + heading(t("record_by_play")))
            for number in sorted(by_play):
                print(bullet(f"play {number}: {record.format_record(by_play[number])}  {dim(game['strategies'][number - 1][:60])}", marker=f"{number}."))
        return 0
    counts = record.tally()
    if not counts:
        print(dim("No outcomes logged yet. Try: log <game> win|loss|draw|mixed [note]"))
        return 0
    names = {g["id"]: g["name"] for g in games}
    print()
    for game_id, row in sorted(counts.items()):
        print(cell(names.get(game_id, game_id), 36, bold) + dim(record.format_record(row)))
    return 0


def cmd_edit(args, games):
    game = find_game(games, args.game)
    path = save_overlay(game)
    print(green(f"Copied '{game['name']}' to {path}"))
    print(dim("Edit that file to change its plays, pitfalls or examples. Changes load on the next start."))
    return 0


def cmd_add_play(args, games):
    game = find_game(games, args.game)
    text = " ".join(args.text).strip()
    if not text:
        raise ValueError("a play needs some text")
    updated = copy.deepcopy(game)
    updated["strategies"] = game["strategies"] + [text]
    path = save_overlay(updated)
    print(green(f"Added play {len(updated['strategies'])} to '{game['name']}' ({path})."))
    return 0


def print_path(title, steps, ending, chance):
    print("\n" + heading(title) + "  " + dim(f"{chance:.0%} {t('chance')}"))
    for number, step in enumerate(steps, 1):
        if step["kind"] == "you":
            print(bullet(f"{step['prompt']}  {bold(step['label'])}", marker=f"{number}."))
        else:
            print(bullet(dim(f"chance: {step['label']} ({step['p']:.0%})"), marker=f"{number}."))
        if step.get("why"):
            print(dim(bullet(t("why") + ": " + step["why"], marker="", indent=5)))
    print_ending(ending, steps)


def print_ending(ending, steps=None):
    styles = {"victory": green, "draw": dim, "failure": red}
    print(styles[ending["outcome"]](t("ending") + ": " + ending["outcome"].upper()))
    if steps:
        last = steps[-1]
        print(dim(f"  {t('followed_last') if last['kind'] == 'you' else t('followed_chance')}: {last['label']}"))
    print(paragraph(ending["text"]))


def play_simulation(sim, save_path=None, resume_path=None, formats=None, hints=None):
    """Play the simulation. With hints on you see the chance of victory and the best strategy.

    Hints start as you choose before the game (or --no-hints). Type h at any choice to turn them on or
    off from that choice on, so you can have hints in one round and none in the next.
    """
    if hints is None:
        hints = True
        if sys.stdin.isatty():
            hints = prompt("Show the chance of victory and the best strategy as you play? (Y/n) ").strip().lower() not in ("n", "no")
    state = {"hints": hints}

    def ask(prompt_text, options):
        while True:
            show = state["hints"]
            best = max(o["chance"] for o in options)
            print("\n" + bold(prompt_text))
            print(dim(f"  b  go back to your previous decision    h  hints {'off' if show else 'on'}"))
            for number, option in enumerate(options, 1):
                chance_text, marker = "", ""
                if show:
                    chance_text = dim(f"{t('chance_from_here')}: {option['chance']:.0%}")
                    marker = green(f" ({t('best')})") if option["chance"] == best else ""
                print(f"  {number}) {option['label']}  {chance_text}{marker}")
            answer = prompt("> ").strip().lower()
            if answer in ("b", "back"):
                return None
            if answer == "h":
                state["hints"] = not show
                print(dim(f"  hints {'on' if state['hints'] else 'off'} from this choice"))
                continue
            if answer.isdigit() and 1 <= int(answer) <= len(options):
                index = int(answer) - 1
                chosen = options[index]
                print(dim(f"  {t('why')}: " + chosen["why"]) if chosen["why"] else "")
                for number, other in enumerate(options, 1):
                    if number - 1 != index and other["why"]:
                        odds = f" ({other['chance']:.0%})" if show else ""
                        print(dim(f"  {t('why_not')} {number}) {other['label']}{odds}: {other['why']}"))
                return index
            print(red(f"  choose a number from 1 to {len(options)}"))

    node, steps = None, None
    if resume_path:
        node, steps = load_state(resume_path, sim)
        print(dim(f"Resuming from a saved game with {len(steps)} step(s) taken."))
    checkpoint = (lambda nid, taken: save_state(save_path, sim, nid, taken)) if save_path else None
    steps, ending = play(sim, ask, say=lambda text: print(dim("  " + text)), node=node, steps=steps, checkpoint=checkpoint)
    if save_path:
        print(dim(f"Your game is saved in {save_path}; resume it with --resume {save_path}."))
    print()
    print_ending(ending, steps)
    if state["hints"]:
        best = solve(sim, "victory")[sim["start"]][0]
        print(dim(t("best_plan_wins", percent=f"{best:.0%}") + f" Run 'sim {sim['id']}' to see it."))
    if formats is None and sys.stdin.isatty():
        formats = ask_formats(prompt)
    if formats:
        folder, written = write_run(sim, steps, ending, formats)
        print(dim(f"Exported to {folder}:"))
        for path in written:
            print(dim(f"  {path.name}"))
    if sys.stdin.isatty() and not resume_path and prompt("Play again from the start? (y/N) ").strip().lower() in ("y", "yes"):
        return play_simulation(sim, formats=formats, hints=hints)
    return 0


def markdown_path(title, steps, ending, chance):
    lines = [f"## {title} ({chance:.0%} chance)", ""]
    for number, step in enumerate(steps, 1):
        if step["kind"] == "you":
            lines.append(f"{number}. {step['prompt']} **{step['label']}**")
        else:
            lines.append(f"{number}. Chance: {step['label']} ({step['p']:.0%})")
        if step.get("why"):
            lines.append(f"   - Why: {step['why']}")
    lines += ["", f"**Ending: {ending['outcome'].upper()}.** {ending['text']}", ""]
    return "\n".join(lines)


def export_simulation(sim, path, win_steps, win_end, win_chance, fail_steps, fail_end, fail_chance):
    every = endings(sim)
    counts = {k: sum(1 for e in every if e["outcome"] == k) for k in ("victory", "draw", "failure")}
    parts = [
        f"# {sim['name']}",
        "",
        f"*Works across: {', '.join(sim['families'])}*",
        "",
        sim["summary"],
        "",
        markdown_path("Path to victory", win_steps, win_end, win_chance),
        markdown_path("Path to failure", fail_steps, fail_end, fail_chance),
        f"## All possible endings",
        "",
        f"- {len(every)} ways to play out: {counts['victory']} victory, {counts['draw']} draw, {counts['failure']} failure.",
        f"- The best plan wins {win_chance:.0%} of the time; the plan most likely to fail, fails {fail_chance:.0%} of the time.",
        "",
        "*Chance steps follow their most likely outcome in each path. Probabilities are illustrative, not measured.*",
        "",
    ]
    Path(path).write_text("\n".join(parts), encoding="utf-8")
    print(green(f"Exported '{sim['name']}' to {path}"))
    return 0


def cmd_sim(args, games):
    sims = load_simulations()
    if args.family:
        wanted = args.family.lower()
        sims = [s for s in sims if any(wanted in f.lower() for f in s["families"])]
        if not sims:
            raise ValueError(f"no simulation covers '{args.family}'. Run 'sim' to list them.")
    if args.mode:
        sims = [s for s in sims if s.get("mode", "basic") == args.mode]
    if not args.id:
        print()
        for sim in sims:
            tag = "[live]" if sim.get("mode") == "live" else "[basic]"
            print(cell(sim["id"], 34, bold) + cell(sim["name"], 42) + dim(tag + " " + ", ".join(sim["families"])))
        print(dim(f"\n{len(sims)} simulation(s). Run 'sim <id>' for the paths to victory and failure, or 'sim <id> --play' to play it."))
        return 0
    if args.matrix:
        game = find_game(games, args.id)
        families = [f["family"] for f in load_areas() if any(game["id"] in sd["games"] for sd in f["subdomains"])]
        sim = matrix_simulation(game, families, opponent=args.opponent, lam=args.lam)
    else:
        sim = find_simulation(sims, args.id)
    sim_name, sim_summary = sim["name"], sim["summary"]
    print(f"\n{bold(sim_name)}")
    print(dim(t("works_across") + ": " + ", ".join(sim["families"])))
    print()
    print(paragraph(sim_summary))
    if args.play or args.resume or args.save:
        formats = parse_formats(args.formats) if args.formats else None
        return play_simulation(sim, save_path=args.save, resume_path=args.resume, formats=formats,
                               hints=False if args.no_hints else None)

    win_steps, win_end, win_chance = trace(sim, solve(sim, "victory"))
    fail_steps, fail_end, fail_chance = trace(sim, solve(sim, "failure"))
    if args.export:
        return export_simulation(sim, args.export, win_steps, win_end, win_chance, fail_steps, fail_end, fail_chance)
    print_path(t("path_victory"), win_steps, win_end, win_chance)
    print_path(t("path_failure"), fail_steps, fail_end, fail_chance)

    every = endings(sim)
    counts = {k: sum(1 for e in every if e["outcome"] == k) for k in ("victory", "draw", "failure")}
    print("\n" + heading(t("all_endings")))
    print(bullet(f"{len(every)} ways to play out, across all of your choices: "
                 f"{counts['victory']} victory, {counts['draw']} draw, {counts['failure']} failure."))
    print(bullet(f"The best plan wins {win_chance:.0%} of the time; the plan most likely to fail, fails {fail_chance:.0%} of the time."))
    print(dim("Chance steps follow their most likely outcome in each path; the percentages cover all branches."))
    return 0


def load_problems():
    return json.loads((DATA_DIR / "problems.json").read_text(encoding="utf-8"))


def cmd_problems(args, games):
    areas = load_problems()
    query = " ".join(args.query).strip().lower()
    by_id = {g["id"]: g for g in games}
    if not query:
        print()
        for area in areas:
            print(bold(area["area"]) + "  " + dim(f"{len(area['problems'])} problems"))
            for item in area["problems"]:
                print(bullet(item["problem"]))
        print(dim("\nRun 'problems <problem or area>' for the best games and their scenarios."))
        return 0

    exact_area = [a for a in areas if a["area"].lower() == query]
    problem_hits = [] if exact_area else [(a, p) for a in areas for p in a["problems"] if query in p["problem"].lower()]
    area_hits = exact_area or [a for a in areas if query in a["area"].lower()]
    if problem_hits:
        for area, item in problem_hits:
            print("\n" + heading(item["problem"]) + "  " + dim(area["area"]))
            print(dim("Best games for this problem, in order:"))
            for number, game_id in enumerate(item["games"], 1):
                game = by_id[game_id]
                print(bullet(f"{game['name']}  {dim(game_id)}", marker=f"{number}."))
                for example in (game.get("examples") or [])[:3]:
                    print("     " + dim("· " + example))
            if item["sims"]:
                print(bullet("Try it: " + ", ".join(f"sim {s}" for s in item["sims"]), marker="→"))
        return 0
    if area_hits:
        area = area_hits[0]
        print("\n" + bold(area["area"]))
        for item in area["problems"]:
            print(bullet(item["problem"]))
        print(dim("\nRun 'problems <problem>' with part of a problem above for the best games."))
        return 0
    raise ValueError(f"no problem or area matches '{query}'. Run 'problems' to list them.")


def cmd_setup(args, games):
    help_data = load_help()
    sims_by_id = {s["id"] for s in load_simulations()}
    if args.all:
        for game in games:
            print(guide_text(game, help_data, sims_by_id))
        return 0
    if not args.game:
        raise ValueError("name a game, e.g. 'setup chicken', or use --all for every game")
    game = find_game(games, " ".join(args.game))
    if args.write:
        path = Path(args.write)
        path.write_text(scenario_template(game), encoding="utf-8")
        print(green(f"Wrote a scenario template for {game['name']} to {path}"))
        print(dim(f"Edit it, then run: advise {path}"))
        return 0
    print(guide_text(game, help_data, sims_by_id))
    return 0


GUIDE_LABELS_EN = {
    "sections": "Guide sections",
    "power_line": "power: {n} principles of strategy, influence and judgement",
    "defend_line": "defend: {n} manipulation tactics and how to recognise and resist them",
    "research_line": "research: {n} steps for research, and starting references",
    "life_line": "life: {n} practical habits for decisions",
    "run_hint": "Run 'guide power', 'guide power 48', or 'guide defend pressure' for details.",
    "defence": "defence",
    "signs": "signs",
    "tested_in": "tested in",
    "no_match_principle": "no principle matches '{query}'",
    "no_match_tactic": "no tactic matches '{query}'",
}


def cmd_guide(args, games):
    guide = json.loads((DATA_DIR / "guide.json").read_text(encoding="utf-8"))
    labels = GUIDE_LABELS_EN | guide.get("labels", {})
    by_id = {g["id"]: g for g in games}
    section = args.section
    query = " ".join(args.query).strip().lower()
    if not section:
        print("\n" + bold(labels["sections"]))
        print(bullet(labels["power_line"].format(n=len(guide["power"]))))
        print(bullet(labels["defend_line"].format(n=len(guide["defend"]))))
        print(bullet(labels["research_line"].format(n=len(guide["research"]))))
        print(bullet(labels["life_line"].format(n=len(guide["life"]))))
        print(dim(guide["note"]))
        print(dim("\n" + labels["run_hint"]))
        return 0
    if section == "power":
        items = guide["power"]
        if query:
            matches = [p for p in items if query == str(p["id"]) or query in p["title"].lower()]
            if not matches:
                raise ValueError(labels["no_match_principle"].format(query=query))
            for p in matches:
                print("\n" + heading(f"{p['id']}. {p['title']}") + "  " + dim(p["area"]))
                print(paragraph(p["principle"]))
                print(bullet(labels["defence"] + ": " + p["defence"], marker="→"))
                for gid in p["games"]:
                    if gid in by_id:
                        print(bullet(f"{labels['tested_in']}: {by_id[gid]['name']}  {dim('sim ' + gid)}", marker="·"))
            return 0
        current = None
        for p in items:
            if p["area"] != current:
                current = p["area"]
                print("\n" + heading(current))
            print(bullet(f"{p['id']}. {p['title']}"))
        return 0
    if section == "defend":
        items = guide["defend"]
        if query:
            matches = [d for d in items if query in d["pattern"].lower()]
            if not matches:
                raise ValueError(labels["no_match_tactic"].format(query=query))
            for d in matches:
                print("\n" + heading(d["pattern"]))
                print(bullet(labels["signs"] + ": " + d["signs"]))
                print(bullet(labels["defence"] + ": " + d["defence"], marker="→"))
            return 0
        for d in items:
            print(bullet(d["pattern"]))
        return 0
    if section == "research":
        print("\n" + heading(t("research_steps")))
        for number, step in enumerate(guide["research"], 1):
            print(bullet(f"{step['step']}: {step['detail']}", marker=f"{number}."))
        print("\n" + heading(t("starting_references")))
        for ref in guide["research_starting_points"]:
            print(bullet(ref))
        return 0
    if section == "life":
        for number, item in enumerate(guide["life"], 1):
            print(bullet(f"{item['title']}: {item['detail']}", marker=f"{number}."))
        return 0
    raise ValueError("sections are power, defend, research and life")


def export_output(argv):
    """Run a command and save its text output as a Markdown file: --export FILE anywhere in the command."""
    import contextlib
    import io
    import re

    index = argv.index("--export")
    if index + 1 >= len(argv):
        print(red("--export needs a file name"), file=sys.stderr)
        return 1
    target = argv[index + 1]
    command = argv[:index] + argv[index + 2:]
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = main(command)
    text = re.sub(r"\x1b\[[0-9;]*m", "", out.getvalue())
    Path(target).write_text(f"# playbook {' '.join(command)}\n\n```\n{text.rstrip()}\n```\n", encoding="utf-8")
    print(green(f"Exported to {target}"))
    return code


def cmd_chart(args, games):
    from . import charts

    kind = args.kind
    if kind == "families":
        svg, name = charts.families_chart(load_areas()), "families"
    elif kind == "traits":
        svg, name = charts.traits_heatmap(games), "traits"
    elif kind == "map":
        svg, name = charts.family_map(load_areas()), "map"
    elif kind == "records":
        counts = record.tally()
        if not counts:
            raise ValueError("no results logged yet. Use: log <game> win|loss|draw|mixed")
        names = {g["id"]: g["name"] for g in games}
        svg, name = charts.records_chart(counts, names), "records"
    elif kind == "plays":
        by_game = {}
        for entry in record.history():
            if entry.get("play"):
                by_game.setdefault((entry["game"], entry["play"]), {}).setdefault(entry["result"], 0)
                by_game[(entry["game"], entry["play"])][entry["result"]] += 1
        if not by_game:
            raise ValueError("no per-play results logged yet. Use: log <game> win|loss --play N")
        names = {g["id"]: g for g in games}
        rows = []
        for (game_id, number), counts in sorted(by_game.items()):
            game = names.get(game_id, {"name": game_id, "strategies": []})
            text = game["strategies"][number - 1] if number <= len(game["strategies"]) else ""
            rows.append((f"{game['name']} - play {number}: {text[:34]}", counts))
        svg, name = charts.plays_chart(rows), "plays"
    elif kind == "sim":
        if not args.target:
            raise ValueError("name a simulation, e.g. 'chart sim chicken'")
        sim = find_simulation(load_simulations(), " ".join(args.target))
        svg, name = charts.sim_tree(sim), f"sim-{sim['id']}"
    else:
        raise ValueError("kinds are families, traits, map, records, plays and sim")
    target = Path(args.out) if args.out else Path("charts") / f"{name}.svg"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(svg, encoding="utf-8")
    print(green(f"Wrote {target}"))
    return 0


def cmd_disable(args, games):
    game = find_game(all_games(), " ".join(args.game))
    set_disabled(game["id"], True)
    print(green(f"Hid '{game['name']}'. Run 'enable {game['id']}' to show it again."))
    return 0


def cmd_enable(args, games):
    game = find_game(all_games(), " ".join(args.game))
    set_disabled(game["id"], False)
    print(green(f"Showing '{game['name']}' again."))
    return 0


def cmd_check(args, games):
    problems = check_overlays()
    if problems:
        for problem in problems:
            print(red("✗ " + problem))
        return 1
    print(green("Your overlay files are valid."))
    return 0


def cmd_unlog(args, games):
    game_id = find_game(games, " ".join(args.game))["id"] if args.game else None
    entry = record.remove_last(game_id)
    if entry is None:
        print(dim("Nothing to remove."))
        return 1
    print(green(f"Removed the last {entry['result']} for {entry['game']} ({entry['date']})."))
    return 0


def all_games():
    """Every built-in game, including ones you have hidden, so they can be shown again."""
    games = []
    for path in sorted(DATA_DIR.glob("*.json")):
        if path.name not in NON_GAME_FILES:
            games.extend(json.loads(path.read_text(encoding="utf-8")))
    return games


def show_theme():
    """Print the current theme with a sample of each colour role."""
    from .ui import _active

    print("\n" + bold("Theme: ") + current_theme())
    samples = {"accent": ("accent", accent), "good": ("victory", good), "bad": ("failure", bad), "mid": ("draw", mid)}
    for role in ROLES:
        label, styler = samples[role]
        colour = _active[role]
        shown = "none" if colour is None else str(colour)
        print("  " + cell(role, 8) + cell(label, 10, styler) + dim(f"colour {shown}"))
    print(dim("\nThemes: " + ", ".join(THEMES) + ".  Change with 'theme <name>', or 'theme set <role> <colour>'."))
    print(dim("Roles: accent, good, bad, mid.  Colours: a name such as red, cyan or orange, or a number 0-255."))
    print(dim("Reset to the default with 'theme reset'.  Turn colour off for one run with NO_COLOR=1."))
    return 0


def cmd_repeat(args, games):
    game = find_game(games, " ".join(args.game))
    if not game.get("matrix"):
        raise ValueError(f"{game['name']} has no payoff table yet, so it cannot be repeated.")
    rounds = check_rounds(args.rounds)
    matrix = game["matrix"]
    formats = parse_formats(args.formats) if args.formats else []
    rows, cols = matrix["rows"], matrix["cols"]
    show_rows, show_cols = rows, cols

    def ask(number, history):
        print("\n" + bold(f"Round {number} of {rounds}. Choose your row:"))
        for index, label in enumerate(show_rows, 1):
            print(f"  {index}) {label}")
        for past_number, (row, col, mine, theirs) in enumerate(history[-3:], len(history) - len(history[-3:]) + 1):
            print(dim(f"  round {past_number}: you {show_rows[row]}, bot {show_cols[col]} (you {mine}, bot {theirs})"))
        while True:
            answer = prompt("> ").strip()
            if answer.isdigit() and 1 <= int(answer) <= len(rows):
                return int(answer) - 1
            print(red(f"  choose a number from 1 to {len(rows)}"))

    def say(number, row, col, mine, theirs):
        print(dim(f"  round {number}: you {show_rows[row]}, bot {show_cols[col]}. You get {mine}, the bot gets {theirs}."))

    print("\n" + bold(game["name"]) + dim(f"  against a {args.opponent} bot, {rounds} round(s)"))
    print(dim(DESCRIPTIONS[args.opponent]))
    try:
        history, total = play_repeated(matrix, rounds, args.opponent, ask, say, seed=args.seed)
    except EOFError:
        print()
        return 0
    best_row, best_total = best_fixed_plan(matrix, rounds, args.opponent, seed=args.seed)
    if formats:
        folder, written = write_repeat(game, args.opponent, rounds, args.seed, history, total, (best_row, best_total))
        print(dim(f"Exported to {folder}: " + ", ".join(written)))
    if args.log:
        result = outcome_for_log(total, best_total)
        record.log_outcome(game["id"], result, note=f"repeated {rounds} rounds vs {args.opponent}, total {total}")
        print(dim(f"Logged as {result} in your records (total {total}, best fixed plan {best_total})."))
    print("\n" + heading("Result"))
    print(f"  Your total: {total} over {rounds} round(s), an average of {total / rounds:.2f} per round.")
    print(f"  Best always-the-same plan against this bot: always {show_rows[best_row]}, total {best_total}.")
    gap = best_total - total
    if gap > 0:
        print(dim(f"  You scored {gap} less than that plan. Look for the bot's pattern in the rounds above."))
    else:
        print(dim("  You matched or beat the best fixed plan."))
    return 0


def cmd_theme(args, games):
    home = playbook_home()
    words = [w.lower() for w in args.words]
    if not words:
        return show_theme()
    if words == ["reset"]:
        reset_theme(home)
        print(dim("Theme reset to classic."))
        return show_theme()
    if words[0] == "set":
        if len(words) != 3 or words[1] not in ROLES:
            raise ValueError("use: theme set <accent|good|bad|mid> <colour>")
        save_theme(home, colours={words[1]: parse_colour(words[2])})
        return show_theme()
    if len(words) == 1 and words[0] in THEMES:
        save_theme(home, name=words[0])
        return show_theme()
    raise ValueError(f"'{' '.join(args.words)}' is not a theme. Themes: {', '.join(THEMES)}.")


HANDLERS = {
    "list": cmd_list,
    "show": cmd_show,
    "advise": cmd_advise,
    "solve": cmd_solve,
    "new": cmd_new,
    "template": cmd_template,
    "areas": cmd_areas,
    "topics": cmd_topics,
    "log": cmd_log,
    "record": cmd_record,
    "edit": cmd_edit,
    "add-play": cmd_add_play,
    "sim": cmd_sim,
    "engine": cmd_engine,
    "problems": cmd_problems,
    "setup": cmd_setup,
    "guide": cmd_guide,
    "chart": cmd_chart,
    "disable": cmd_disable,
    "enable": cmd_enable,
    "check": cmd_check,
    "unlog": cmd_unlog,
    "theme": cmd_theme,
    "keywords": cmd_keywords,
    "help": cmd_help,
    "version": cmd_version,
    "tools": cmd_tools,
    "tool": cmd_tool,
    "repeat": cmd_repeat,
}


def build_parser():
    parser = argparse.ArgumentParser(
        prog="playbook",
        description="Game theory playbook: identify the game behind a situation and how to play it.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    ls = sub.add_parser("list", help="list games")
    ls.add_argument("--domain", choices=sorted(DOMAIN_WORDS), help="only games that fit this domain")
    ls.add_argument("--search", help="text to look for across all game fields")

    show = sub.add_parser("show", help="explain one game and its playbook")
    show.add_argument("game", help="game id or name, e.g. chicken")
    show.add_argument("--formats", metavar="LIST", help="export the game card: md, json or both (e.g. md,json)")

    advise = sub.add_parser("advise", help="match a situation to games and get playbook rules")
    advise.add_argument("file", nargs="?", help="scenario file (see 'template')")
    advise.add_argument("-d", "--describe", help="plain-English description of the situation")
    advise.add_argument("--set", action="append", metavar="KEY=VALUE",
                        help="set or override a trait, e.g. --set timing=sequential (repeatable)")
    advise.add_argument("--top", type=int, default=3, help="how many games to rank (default 3)")

    solve = sub.add_parser("solve", help="analyse a two-player payoff matrix")
    solve.add_argument("matrix", help='rows separated by ";", cells "yours,theirs", e.g. "3,3 0,5; 5,0 1,1"')
    solve.add_argument("--json", action="store_true", help="print the solution as JSON")
    solve.add_argument("--rows", help="comma-separated names for your actions")
    solve.add_argument("--cols", help="comma-separated names for their actions")

    new = sub.add_parser("new", help="build a scenario file with prompts")
    new.add_argument("path", nargs="?", default="scenario.gt")

    sub.add_parser("template", help="print the scenario file syntax")
    sub.add_parser("menu", help="open the numbered main menu")

    areas = sub.add_parser("areas", help="browse game families, sub-domains and reading lists")
    areas.add_argument("name", nargs="*", help="family name or part of it, e.g. war")

    topics = sub.add_parser("topics", help="browse the games by topic, such as business or military")
    topics.add_argument("name", nargs="*", help="topic name or part of it, e.g. military")

    log = sub.add_parser("log", help="record the outcome of a game you played")
    log.add_argument("game", help="game id or name")
    log.add_argument("result", choices=record.RESULTS)
    log.add_argument("note", nargs="*", help="optional note")
    log.add_argument("--play", type=int, help="which play you used, by its number in 'show'")

    rec = sub.add_parser("record", help="show win and loss records")
    rec.add_argument("game", nargs="?", help="game id or name, for its full history")
    rec.add_argument("--csv", metavar="FILE", help="save every logged result as CSV")
    rec.add_argument("--json", action="store_true", help="print the records as JSON")

    edit = sub.add_parser("edit", help="copy a game into your playbook folder to edit its plays")
    edit.add_argument("game", help="game id or name")

    add_play = sub.add_parser("add-play", help="append a play to a game in your playbook folder")
    add_play.add_argument("game", help="game id or name")
    add_play.add_argument("text", nargs="+", help="the play, in your own words")

    setup = sub.add_parser("setup", help="how to set up a custom scenario for a game")
    setup.add_argument("game", nargs="*", help="game id or name")
    setup.add_argument("--all", action="store_true", help="print the guide for every game")
    setup.add_argument("--write", metavar="FILE", help="save an editable scenario template for the game")

    guide = sub.add_parser("guide", help="48 principles of strategy and influence, manipulation defence, research and life habits")
    guide.add_argument("section", nargs="?", choices=["power", "defend", "research", "life"])
    guide.add_argument("query", nargs="*", help="a principle number or title, or a tactic name")

    chart = sub.add_parser("chart", help="draw an SVG chart or map: families, traits, map, records, or sim <id>")
    chart.add_argument("kind", choices=["families", "traits", "map", "records", "plays", "sim"])
    chart.add_argument("target", nargs="*", help="for 'sim': the simulation id")
    chart.add_argument("--out", help="where to save the SVG (default: charts/<name>.svg)")

    for name, text in (("disable", "hide a game from the playbook without deleting it"), ("enable", "show a hidden game again")):
        cmd = sub.add_parser(name, help=text)
        cmd.add_argument("game", nargs="+", help="game id or name")
    sub.add_parser("check", help="check your overlay files for problems")
    sub.add_parser("help", help="show every command and how to use it")
    sub.add_parser("version", help="print the version")
    sub.add_parser("tools", help="list the tools other programs can call, with their input schemas")
    tool_cmd = sub.add_parser("tool", help="run one tool with JSON arguments, e.g. tool find_games '{\"description\": \"price war\"}'")
    tool_cmd.add_argument("name", help="the tool name, from 'playbook tools'")
    tool_cmd.add_argument("arguments", nargs="?", default="{}", help="the arguments as a JSON object")
    kw_cmd = sub.add_parser("keywords", help="say which games and areas a description points to, from its words")
    kw_cmd.add_argument("words", nargs="+", help="a few words describing the situation")
    repeat_cmd = sub.add_parser("repeat", help="play a payoff matrix for 1 to 50 rounds against a bot that remembers the game")
    repeat_cmd.add_argument("game", nargs="+", help="game id or name")
    repeat_cmd.add_argument("--rounds", type=int, default=10, help="how many rounds, 1 to 50 (default 10)")
    repeat_cmd.add_argument("--opponent", choices=OPPONENTS, default="tit-for-tat", help="the bot's rule (default tit-for-tat)")
    repeat_cmd.add_argument("--seed", type=int, default=1, help="seed for the random bot, so a run can be repeated")
    repeat_cmd.add_argument("--formats", metavar="LIST", help="export the run: md, json or both (e.g. md,json)")
    repeat_cmd.add_argument("--log", action="store_true", help="add the result to your records (win, draw or loss against the best fixed plan)")
    theme_cmd = sub.add_parser("theme", help="change the colours and look: theme <name>, or theme set <role> <colour>")
    theme_cmd.add_argument("words", nargs="*", help="a theme name, 'set <role> <colour>', or 'reset'")
    unlog = sub.add_parser("unlog", help="remove the most recent logged result")
    unlog.add_argument("game", nargs="*", help="only for this game (optional)")

    problems = sub.add_parser("problems", help="find the best games for a problem, with scenarios")
    problems.add_argument("query", nargs="*", help="a problem or an area, e.g. work; omit to list all")

    engine_parser = sub.add_parser("engine", help="play a computer opponent that adapts to you")
    engine_parser.add_argument("name", nargs="*", help="engine game id, e.g. nim; omit to list them")

    sim = sub.add_parser("sim", help="simulations: paths to victory and failure, or play one")
    sim.add_argument("id", nargs="?", help="simulation id or name; omit to list them")
    sim.add_argument("--play", action="store_true", help="play it yourself")
    sim.add_argument("--family", help="only simulations that apply to this area, e.g. war or work")
    sim.add_argument("--mode", choices=["basic", "live"],
                     help="basic: fixed choices you can read and play; live: an opponent replies to each move")
    sim.add_argument("--export", metavar="FILE", help="save the paths and endings as a Markdown file")
    sim.add_argument("--matrix", action="store_true", help="build the simulation from this game's payoff matrix")
    sim.add_argument("--opponent", choices=["equilibrium", "uniform", "noisy", "loss-averse"], default="equilibrium",
                     help="with --matrix: equilibrium play, uniform random, a noisy best responder, or a loss-averse one")
    sim.add_argument("--lam", type=float, default=2.0,
                     help="with --opponent noisy: how sharply they pick the better option (0 is random)")
    sim.add_argument("--save", metavar="FILE", help="save your game as you play, so you can resume it")
    sim.add_argument("--resume", metavar="FILE", help="continue a game saved with --save")
    sim.add_argument("--no-hints", action="store_true", help="hide the chance of victory and the best strategy while you play")
    sim.add_argument("--formats", metavar="LIST", help="export the run after playing: md, json, csv, svg or all (e.g. md,csv)")
    return parser


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    load_theme(playbook_home())
    if "--export" in argv and argv and argv[0] != "sim":
        return export_output(argv)
    if not argv:
        from .repl import run_launch

        return run_launch(load_games())
    if argv[0] == "menu":
        from .repl import run_menu_program

        return run_menu_program(load_games())
    args = build_parser().parse_args(argv)
    if args.command == "check":
        return cmd_check(args, None)
    try:
        return HANDLERS[args.command](args, load_games())
    except (ValueError, OSError) as exc:
        print(red(f"error: {exc}"), file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        print()
        return 130
