"""Interactive session.

Plain text describes a situation and gets matched to games. Lines starting with
'/' are commands. The same handlers back the subcommands in cli.py.
"""

import argparse
import contextlib
import io
import shlex
import sys

from . import advisor, cli, keywords, record
from .catalog import find_game, load_areas, load_topics, playbook_home
from .scenario import describe
from . import lineedit
from .i18n import t
from .ui import accent, bold, box, dim, good, green, heading, red, visible_width
from shlex import quote

VERSION = cli.VERSION

# Commands that reuse the subcommand parser and handlers.
DELEGATED = {"list", "show", "solve", "new", "template", "areas", "topics", "log", "record", "edit", "add-play", "sim", "engine", "problems", "setup", "guide", "chart", "disable", "enable", "check", "unlog", "theme", "repeat", "keywords"}


COMMANDS = sorted(
    ["/" + name for name in ("list", "show", "advise", "set", "unset", "scenario", "clear", "solve", "new", "template",
                             "areas", "topics", "log", "record", "edit", "add-play", "sim", "engine", "problems", "setup", "guide", "chart",
                             "disable", "enable", "check", "unlog", "theme", "repeat", "keywords", "claude", "menu", "cls", "help", "quit")]
)


def _setup_line_editing(games):
    """Command history saved in the playbook home, and tab completion for commands and game ids."""
    try:
        import readline
    except ImportError:
        return None
    from .catalog import playbook_home

    history_file = playbook_home() / "history"
    try:
        readline.read_history_file(history_file)
    except OSError:
        pass
    words = COMMANDS + [g["id"] for g in games]

    def complete(text, state):
        matches = [w for w in words if w.startswith(text)]
        return matches[state] if state < len(matches) else None

    readline.set_completer(complete)
    readline.set_completer_delims(" \t")
    readline.parse_and_bind("tab: complete")
    return readline, history_file


EDITOR = None

# Commands that ask questions, play a game, or save one print straight to the terminal.
INTERACTIVE = {"menu", "new", "cls"}


def _phrase_completer(games):
    from . import advisor, keywords

    phrases = keywords.phrase_list(keywords.load_keywords(), combinations=advisor.load_combinations())

    def complete(text):
        return keywords.complete_phrase(text, phrases)

    return complete


def _completer(games):
    from . import advisor, keywords

    words = COMMANDS + [g["id"] for g in games]
    vocabulary = keywords.vocabulary(games, combinations=advisor.load_combinations())

    def complete(prefix):
        if prefix.startswith("/") or not prefix:
            return [w for w in words if w.startswith(prefix)]
        ids = [g["id"] for g in games if g["id"].startswith(prefix)]
        return ids + keywords.complete_word(prefix, vocabulary)

    return complete


def run(games):
    global EDITOR
    from .catalog import playbook_home

    print_banner()
    session = Session(games)
    EDITOR = lineedit.Editor(history_path=playbook_home() / "history", complete=_completer(games),
                             complete_phrase=_phrase_completer(games))
    try:
        return _loop(session, games)
    finally:
        try:
            EDITOR.save_history()
        except OSError:
            pass


def _should_page(line):
    words = line.split()
    if not words or words[0].lstrip("/") in INTERACTIVE:
        return False
    return not any(w in ("--play", "--resume", "--save") for w in words)


def run_paged(line, action):
    """Run an action with its output captured. Long output is scrolled with the pager."""
    if not _should_page(line):
        return action()
    buffer = io.StringIO()
    error = None
    with contextlib.redirect_stdout(buffer):
        try:
            result = action()
        except (SystemExit, ValueError, OSError) as exc:
            error = exc
            result = False
    text = buffer.getvalue()
    if text:
        lineedit.page(text) if text.count("\n") >= lineedit.terminal_rows() - 2 else sys.stdout.write(text)
    if error is not None:
        raise error
    return result


def _loop(session, games):
    while True:
        line, ok = EDITOR.read_line(accent("❯ "))
        if not ok:
            print()
            return 0
        line = line.strip()
        if not line:
            continue
        try:
            if line.startswith("/"):
                if run_paged(line, lambda: session.command(line[1:])):
                    return 0
            else:
                run_paged(line, lambda: session.describe(line))
        except SystemExit:
            # argparse has already printed its message; keep the session going.
            continue
        except (ValueError, OSError) as exc:
            print(red("✗ " + str(exc)))


# The name in three rows of block letters: bigger than plain text, with no artwork.
WORDMARK = [
    "█▀▀ █▀█ █▀▀ ▄▀█ █   █▀▀ ▀█▀ ▄▀▄ █▄ █",
    "█▀  █▀▄ █▄█ █▀█ █   █▀   █  █ █ █ ▀█",
    "█▄▄ ▀ ▀ ▀▀▀ ▀ ▀ █▄▄ █▄▄ ▄█▄ ▀▄▀ ▀  ▀",
]


def app_box_lines():
    """The text inside the green app box: the name in block letters, then the version."""
    cols = lineedit.terminal_columns() if lineedit.is_terminal() else 80
    width = min(cols, 120) - 4
    rows = [bold(accent(line)) for line in WORDMARK]
    rows.append("  " + dim("Game Theory Playbook") + "  v" + VERSION)
    return [row + " " * max(0, width - visible_width(row)) for row in rows]


def print_banner():
    lines = [
        *app_box_lines(),
        "",
        "Describe a situation in plain English, or type /help.",
        "Type /menu to browse games, simulations, advice, solving and more.",
    ]
    print(box(lines, border=green))
    print(dim("  e.g.  two companies set prices at the same time, once only"))
    print()


class Session:
    def __init__(self, games):
        self.games = games
        self.scenario = cli.new_scenario()

    def describe(self, text):
        """Read a plain-English situation, replace the current one, and advise."""
        try:
            game = find_game(self.games, text)
        except ValueError:
            game = None
        if game:
            cli.cmd_show(argparse.Namespace(game=game["id"]), self.games)
            return
        sc = describe(text)
        self.scenario = sc
        cli.show_inferred(sc)
        cli.print_advice(sc, self.games, 3)

    def command(self, line):
        """Run one slash command. Returns True when the session should end."""
        parts = shlex.split(line)
        if not parts:
            return False
        name, args = parts[0], parts[1:]

        if name in ("help", "h", "?"):
            print_help()
        elif name in ("quit", "exit", "q"):
            return True
        elif name in DELEGATED:
            namespace = cli.build_parser().parse_args([name] + args)
            cli.HANDLERS[name](namespace, self.games)
        elif name == "advise":
            namespace = cli.build_parser().parse_args(["advise"] + args)
            if namespace.file or namespace.describe:
                self.scenario = cli.scenario_from_args(file=namespace.file, describe_text=namespace.describe)
            cli.apply_sets(self.scenario, namespace.set or [])
            cli.print_advice(self.scenario, self.games, namespace.top)
        elif name == "set":
            if not args:
                raise ValueError("usage: /set key=value [key=value ...]")
            cli.apply_sets(self.scenario, args)
            cli.print_advice(self.scenario, self.games, 3)
        elif name == "unset":
            if not args:
                raise ValueError("usage: /unset key [key ...]")
            for key in args:
                self.scenario["traits"].pop(key.lower(), None)
            cli.print_advice(self.scenario, self.games, 3)
        elif name == "scenario":
            self.show_scenario()
        elif name == "menu":
            return run_menu(self)
        elif name == "clear":
            self.scenario = cli.new_scenario()
            print(dim("Situation cleared."))
        elif name == "claude":
            self.claude(args)
        elif name == "cls":
            _clear()
            print_banner()
        else:
            raise ValueError(f"unknown command /{name}. Type /help for the list")
        return False

    def claude(self, args):
        """/claude on|off|status, then ask, game, sim or scenario. Off unless switched on."""
        from . import claude

        action, rest = (args[0], args[1:]) if args else ("help", [])
        if action in ("on", "off"):
            claude.set_on(action == "on")
            if action == "on":
                print(bold("Claude is on.") + " Questions go to Anthropic when you ask one, nothing else is sent.")
                print(dim("Sent with each question: your question, and the text of the game, simulation or situation you named."))
                print(dim("Model: " + claude.model() + ". Type /claude off to stop."))
            else:
                print(dim("Claude is off. Nothing is sent."))
        elif action == "status":
            print(f"Claude: {'on' if claude.is_on() else 'off'} · key: {'set' if claude.api_key() else 'not set'} · model: {claude.model()}")
        elif action == "ask":
            self.ask_claude(" ".join(rest), [("Situation", self.situation_text())])
        elif action == "game":
            if not rest:
                raise ValueError("usage: /claude game <game> <question>")
            game = find_game(self.games, rest[0])
            self.ask_claude(" ".join(rest[1:]), [("Game", claude.game_part(game))])
        elif action == "sim":
            if len(rest) < 2:
                raise ValueError("usage: /claude sim <simulation> <question>")
            from .sim import find_simulation, load_simulations

            sim = find_simulation(load_simulations(), rest[0])
            self.ask_claude(" ".join(rest[1:]), [("Simulation", claude.simulation_part(sim))])
        elif action == "scenario":
            if not self.scenario["traits"] and not self.scenario.get("text"):
                raise ValueError("describe a situation first, then ask /claude scenario <question>")
            hits = advisor.rank_games(self.games, self.scenario["traits"], self.scenario["domains"], top=3,
                                      records=record.tally(), text=self.scenario.get("text", ""),
                                      keyword_data=keywords.load_keywords())
            games_text = "\n\n".join(claude.game_part(hit["game"]) for hit in hits if hit["score"] > 0)
            self.ask_claude(" ".join(rest), [("Situation and matching games", claude.scenario_part(
                self.scenario.get("text") or cli.format_traits(self.scenario["traits"]), games_text))])
        else:
            print(bold("Claude help"))
            for line in ("/claude on | off | status", "/claude ask <question>      the current situation and your question",
                         "/claude game <game> <question>", "/claude sim <simulation> <question>",
                         "/claude scenario <question>   the current situation with its top matching games"):
                print("  " + line)

    def situation_text(self):
        parts = [self.scenario.get("text", "")] if self.scenario.get("text") else []
        if self.scenario["traits"]:
            parts.append(cli.format_traits(self.scenario["traits"]))
        return "\n".join(parts)

    def ask_claude(self, question, parts):
        from . import claude

        if not question.strip():
            raise ValueError("type a question after the command")
        claude.check_ready()
        answer, sent = claude.ask(question, parts)
        print(dim(f"Sent {sent} characters to {claude.model()}."))
        print("\n" + heading("Claude"))
        print(paragraph_text(answer))

    def show_scenario(self):
        if not self.scenario["traits"]:
            print(dim("No situation yet. Describe one in plain English, or use /set key=value."))
            return
        print(bold(self.scenario["title"] or "Current situation"))
        print(dim(cli.format_traits(self.scenario["traits"])))
        if self.scenario["domains"]:
            print(dim("domains: " + ", ".join(self.scenario["domains"])))


def paragraph_text(text):
    return "\n".join(cli.paragraph(line) if line.strip() else "" for line in text.split("\n"))


def print_help():
    print("\n" + heading("Commands"))
    rows = [
        ("/list [domain]", "list games, optionally for one domain"),
        ("/show <game>", "explain a game and its playbook"),
        ("/advise [file.gt]", "rank games for the current or a loaded situation"),
        ("/set key=value ...", "set or override traits on the current situation"),
        ("/unset key ...", "remove traits from the current situation"),
        ("/scenario", "show the current situation"),
        ('/solve "a,b c,d; …"', "analyse a payoff matrix"),
        ("/new [file.gt]", "build a scenario file with guided prompts"),
        ("/template", "print the scenario file syntax"),
        ("/clear", "forget the current situation"),
        ("/help", "show this list"),
        ("/menu", "open the full menu: games, simulations, advice, solving, Claude, colours"),
        ("/cls", "clear the screen and show the banner again"),
        ("/claude on|ask|game|sim|scenario", "ask Claude about a game or simulation (opt-in)"),
        ("/quit", "leave the session"),
    ]
    for command, text in rows:
        print("  " + cli.cell(command, 26, bold) + dim(text))
    print("\n" + dim("Or just type a situation in plain English. The playbook matches it to games and gives the rules to play."))


MENU_ITEMS = ["menu_games", "menu_simulations", "menu_engine", "menu_advise", "menu_solve", "menu_areas", "menu_topics", "menu_guide",
              "menu_records", "menu_repeat", "menu_claude", "menu_theme", "menu_quit"]


def print_menu():
    print("\n" + heading(t("menu_title")))
    print(f"  0) {t('menu_command')}")
    for number, key in enumerate(MENU_ITEMS, 1):
        print(f"  {number}) {t(key)}")


MENU_DETAILS = {
    "menu_games": "detail_games", "menu_simulations": "detail_simulations", "menu_engine": "detail_engine",
    "menu_advise": "detail_advise",
    "menu_solve": "detail_solve", "menu_areas": "detail_areas", "menu_topics": "detail_topics", "menu_guide": "detail_guide",
    "menu_records": "detail_records", "menu_repeat": "detail_repeat",
    "menu_theme": "detail_theme", "menu_claude": "detail_claude",
    "menu_quit": "detail_quit", "menu_command": "detail_command",
}


def _quote(text):
    return quote(text)


def _captured_view(session, line):
    """Run a session command with its output captured, then show it full screen until q."""
    buffer = io.StringIO()
    error = None
    with contextlib.redirect_stdout(buffer):
        try:
            session.command(line)
        except SystemExit:
            pass
        except (ValueError, OSError) as exc:
            error = exc
    text = buffer.getvalue()
    if error is not None:
        text += red("✗ " + str(error)) + "\n"
    lineedit.view(text)


def _plain(session, line):
    """Run an interactive command on the terminal, then wait for Enter."""
    sys.stdout.write("\x1b[?1049l\x1b[H\x1b[2J")
    try:
        session.command(line)
    except SystemExit:
        pass
    except (ValueError, OSError) as exc:
        print(red("✗ " + str(exc)))
    input(dim("\n" + t("press_enter") + " "))


def _clear():
    sys.stdout.write("\x1b[H\x1b[2J")
    sys.stdout.flush()


def _menu_games(session):
    items = [(g["name"], g["summary"] + " " + dim(g["category"])) for g in session.games]
    while True:
        index, _ = lineedit.pick(heading(t("pick_game")), items)
        if index < 0:
            return
        _captured_view(session, f"show {_quote(session.games[index]['id'])}")


def _menu_simulations(session):
    from .sim import load_simulations

    sims = load_simulations()
    items = [(sim["name"], sim["summary"] + " " + t("works_across") + ": " + ", ".join(sim["families"])) for sim in sims]
    while True:
        index, key = lineedit.pick(heading(t("pick_sim")), items, {"p": t("play")})
        if index < 0:
            return
        if key == "p":
            _plain(session, f"sim {_quote(sims[index]['id'])} --play")
        else:
            _captured_view(session, f"sim {_quote(sims[index]['id'])}")


def _menu_engine(session):
    """The engine games: you play a computer opponent that adapts as you play."""
    from .engine import engine_games

    games = engine_games()
    items = [(game["name"], game["summary"]) for game in games]
    while True:
        index, _ = lineedit.pick(heading(t("pick_engine")), items)
        if index < 0:
            return
        _plain(session, f"engine {_quote(games[index]['id'])}")


def _menu_families(session):
    areas = load_areas()
    items = [(area["family"], area["summary"]) for area in areas]
    while True:
        index, key = lineedit.pick(heading(t("pick_family")), items, {"p": t("problems")})
        if index < 0:
            return
        if key == "p":
            _captured_view(session, "problems")
        else:
            _menu_family_games(session, areas[index])


def _menu_topics(session):
    """The topics: each one lists its games, which you can play or simulate."""
    topics = load_topics()
    items = [(topic["name"], topic["summary"]) for topic in topics]
    while True:
        index, _ = lineedit.pick(heading(t("pick_topic")), items)
        if index < 0:
            return
        _menu_topic_games(session, topics[index])


def _menu_topic_games(session, topic):
    """List the games in a topic, each with its place in the families. Play and simulate work as in a family."""
    from .sim import load_simulations

    has_sim = {sim["id"] for sim in load_simulations()}
    places = cli.game_locations()
    games = cli.topic_games(session.games, topic["id"])
    items = [(game["name"], places.get(game["id"], "") + ". " + game["summary"]) for game in games]
    while True:
        index, key = lineedit.pick(heading(topic["name"]), items, {"s": t("simulate"), "p": t("play")})
        if index < 0:
            return
        game_id = games[index]["id"]
        if key == "s":
            _captured_view(session, _sim_line(game_id, game_id in has_sim, False))
        elif key == "p":
            _plain(session, _sim_line(game_id, game_id in has_sim, True))
        else:
            _captured_view(session, f"show {_quote(game_id)}")


def _menu_family_games(session, family):
    """List every game in a family. Each game can be played or simulated; games without
    their own simulation use their payoff table."""
    from .sim import load_simulations

    has_sim = {sim["id"] for sim in load_simulations()}
    by_id = {game["id"]: game for game in session.games}
    ids, items = [], []
    for sub in family["subdomains"]:
        for game_id in sub["games"]:
            if game_id in by_id:
                ids.append(game_id)
                items.append((by_id[game_id]["name"], sub["name"] + ". " + by_id[game_id]["summary"]))
    extra = {"s": t("simulate"), "p": t("play"), "a": t("family_overview")}
    while True:
        index, key = lineedit.pick(heading(family["family"]), items, extra)
        if index < 0:
            return
        game_id = ids[index]
        if key == "s":
            _captured_view(session, _sim_line(game_id, game_id in has_sim, False))
        elif key == "p":
            _plain(session, _sim_line(game_id, game_id in has_sim, True))
        elif key == "a":
            _captured_view(session, f"areas {_quote(family['family'])}")
        else:
            _captured_view(session, f"show {_quote(game_id)}")


def _sim_line(game_id, has_sim, play):
    """The sim command for a game: its own simulation when it has one, else its payoff table."""
    line = f"sim {_quote(game_id)}" + ("" if has_sim else " --matrix")
    return line + (" --play" if play else "")


def _menu_guide(session):
    items = [(t("guide_power"), t("detail_guide")), (t("guide_defend"), t("detail_guide")),
             (t("research_steps"), t("detail_guide")), (t("guide_life"), t("detail_guide")),
             (t("setup_game"), t("pick_setup"))]
    sections = ["power", "defend", "research", "life"]
    while True:
        index, _ = lineedit.pick(heading(t("pick_guide")), items)
        if index < 0:
            return
        if index < len(sections):
            _captured_view(session, f"guide {sections[index]}")
            continue
        game_index, _ = lineedit.pick(heading(t("pick_setup")), [
            (g["name"], g["summary"]) for g in session.games])
        if game_index >= 0:
            _captured_view(session, f"setup {_quote(session.games[game_index]['id'])}")


def _menu_records(session):
    items = [(t("my_records"), t("detail_records")), (t("record_chart"), t("detail_records")),
             (t("play_chart"), t("detail_records"))]
    commands = ["record", "chart records", "chart plays"]
    while True:
        index, _ = lineedit.pick(heading(t("menu_records")), items)
        if index < 0:
            return
        _captured_view(session, commands[index])


def _menu_repeat(session):
    """Pick a game with a payoff table, how many rounds, and the bot to play against."""
    from .repeat import DESCRIPTIONS, OPPONENTS

    games = [g for g in session.games if g.get("matrix")]
    index, _ = lineedit.pick(heading(t("pick_repeat")), [(g["name"], g["summary"]) for g in games])
    if index < 0:
        return
    game = games[index]
    opponent_index, _ = lineedit.pick(heading(t("pick_bot")), [(name, DESCRIPTIONS[name]) for name in OPPONENTS])
    if opponent_index < 0:
        return
    rounds = input(t("ask_rounds") + " [10]: ").strip() or "10"
    session.command(f"repeat {game['id']} --rounds {rounds} --opponent {OPPONENTS[opponent_index]} --log")


THEME_DETAILS = {
    "classic": "Orange headings, green victories, red failures, grey draws.",
    "ocean": "Blue headings, cyan victories, coral failures, soft yellow draws.",
    "forest": "Green headings, bright green victories, rust failures, olive draws.",
    "contrast": "Bright yellow headings, vivid green and red, white draws.",
    "sunset": "Coral headings, gold victories, plum failures, tan draws.",
    "midnight": "Lavender headings, sky-blue victories, pink failures, slate draws.",
    "rose": "Pink headings, sage victories, deep red failures, pale draws.",
    "matrix": "Bright green headings and victories, red failures, dark green draws.",
    "paper": "Brown headings, olive victories, red failures, tan draws.",
    "claude-dark": "Dark background with Claude's warm orange headings, soft green wins, clay-red losses.",
    "claude-light": "For light backgrounds: deep orange headings, forest green wins, brick-red losses.",
    "plain": "Neutral grey colours with plain ASCII box edges, for old terminals and fonts.",
    "mono": "No colour: bold headings only, for plain or high-contrast screens.",
}


def _menu_claude(session):
    """Ask Claude about a game, a simulation or the situation, or switch it on or off."""
    options = [(t("claude_game"), t("detail_claude_game")), (t("claude_sim"), t("detail_claude_sim")),
               (t("claude_scenario"), t("detail_claude_scenario")), (t("claude_on"), t("detail_claude_on")),
               (t("claude_off"), t("detail_claude_off"))]
    while True:
        index, _ = lineedit.pick(heading(t("menu_claude")), options)
        if index < 0:
            return
        if index == 0:
            game_index, _ = lineedit.pick(heading(t("pick_game")), [(g["name"], g["summary"]) for g in session.games])
            if game_index < 0:
                continue
            question = _question()
            if question:
                _captured_view(session, f"claude game {_quote(session.games[game_index]['id'])} {_quote(question)}")
        elif index == 1:
            from .sim import load_simulations

            sims = load_simulations()
            sim_index, _ = lineedit.pick(heading(t("pick_sim")), [(s["name"], s["summary"]) for s in sims])
            if sim_index < 0:
                continue
            question = _question()
            if question:
                _captured_view(session, f"claude sim {_quote(sims[sim_index]['id'])} {_quote(question)}")
        elif index == 2:
            question = _question()
            if question:
                _captured_view(session, f"claude scenario {_quote(question)}")
        elif index == 3:
            _captured_view(session, "claude on")
        else:
            _captured_view(session, "claude off")


def _question():
    _clear()
    return input(t("ask_claude_question") + ": ").strip()


def _menu_theme(session):
    names = list(THEME_DETAILS)
    index, _ = lineedit.pick(heading(t("pick_theme")), [(name, THEME_DETAILS[name]) for name in names])
    if index >= 0:
        session.command(f"theme {names[index]}")

def run_menu(session, back_quits=False):
    """Runs the main menu. End of input quits the program, as it does at the prompt.

    back_quits is True at launch, where backing out of the menu means leaving the program.
    """
    try:
        return _run_menu(session, back_quits)
    except EOFError:
        print()
        return True


def menu_title():
    """The green app box above the main menu."""
    return box(app_box_lines(), border=green) + "\n" + heading(t("menu_title"))


def _run_menu(session, back_quits):
    """The main menu: a full-screen list with a description of each entry.

    Each entry opens its own list, and results open full screen, so q always returns to where you were.
    Returns True when the user chooses to quit the program, False to go back to the session.
    """
    while True:
        entries = ["menu_command"] + MENU_ITEMS
        items = [(t(key) if n == 0 else f"{n}) {t(key)}", t(MENU_DETAILS[key])) for n, key in enumerate(entries)]
        index, _ = lineedit.pick(menu_title(), items)
        if index == lineedit.NOT_TERMINAL:
            return _run_menu_typed(session)
        if index < 0:
            return back_quits
        key = entries[index]
        if key == "menu_command":
            return False
        if key == "menu_games":
            _menu_games(session)
        elif key == "menu_simulations":
            _menu_simulations(session)
        elif key == "menu_engine":
            _menu_engine(session)
        elif key == "menu_advise":
            _ask_and_show(session, t("ask_situation") + ": ", lambda text: f"advise -d {_quote(text)}")
        elif key == "menu_solve":
            _ask_and_show(session, t("ask_matrix") + ": ", lambda text: f"solve {_quote(text)}")
        elif key == "menu_areas":
            _menu_families(session)
        elif key == "menu_topics":
            _menu_topics(session)
        elif key == "menu_guide":
            _menu_guide(session)
        elif key == "menu_records":
            _menu_records(session)
        elif key == "menu_repeat":
            _menu_repeat(session)
        elif key == "menu_claude":
            _menu_claude(session)
        elif key == "menu_theme":
            _menu_theme(session)
        elif key == "menu_quit":
            return True


def _ask_and_show(session, prompt, build_line):
    """Ask a question, show the answer full screen, then offer to try again before the menu returns."""
    while True:
        _clear()
        text = input(prompt).strip()
        if not text:
            return
        _captured_view(session, build_line(text))
        if input(t("try_again") + ": ").strip().lower() not in ("t", "try", "y", "yes"):
            return


def _run_menu_typed(session):
    """A numbered menu over the whole playbook. Each choice runs the same command you could type.

    Returns True when the user chooses to quit the program, False to go back to the session.
    """
    while True:
        picked = lineedit.NOT_TERMINAL
        if picked == -1:
            return False
        if picked >= 0:
            choice = str(picked + 1)
        else:
            print_menu()
            choice = input(accent("\u276f ") + t("menu_prompt") + ": ").strip()
        if choice in ("", "0", "b", "back"):
            return False
        key = MENU_ITEMS[int(choice) - 1] if choice.isdigit() and 0 < int(choice) <= len(MENU_ITEMS) else ""
        if key == "menu_quit":
            return True
        line = None
        if key == "menu_games":
            text = input(t("ask_game") + ": ").strip()
            line = f"show {quote(text)}" if text else "list"
        elif key == "menu_simulations":
            text = input(t("ask_sim") + ": ").strip()
            if not text:
                line = "sim"
            else:
                mode = input(t("ask_sim_mode") + ": ").strip()
                line = {"1": f"sim {quote(text)}", "2": f"sim {quote(text)} --play",
                        "3": f"sim {quote(text)} --matrix", "4": f"sim {quote(text)} --matrix --play"}.get(mode)
        elif key == "menu_engine":
            text = input(t("pick_engine") + ": ").strip()
            line = f"engine {quote(text)}" if text else "engine"
        elif key == "menu_advise":
            text = input(t("ask_situation") + ": ").strip()
            line = f"advise -d {quote(text)}" if text else None
        elif key == "menu_solve":
            text = input(t("ask_matrix") + ": ").strip()
            line = f"solve {quote(text)}" if text else None
        elif key == "menu_areas":
            text = input(t("ask_query") + ": ").strip()
            line = f"problems {quote(text)}" if text else "areas"
        elif key == "menu_topics":
            text = input(t("ask_topic") + ": ").strip()
            line = f"topics {quote(text)}" if text else "topics"
        elif key == "menu_guide":
            mode = input(t("ask_guide") + ": ").strip()
            if mode == "1":
                section = input(t("ask_guide_section") + ": ").strip()
                line = f"guide {section}".strip()
            elif mode == "2":
                text = input(t("ask_game") + ": ").strip()
                line = f"setup {quote(text)}" if text else None
        elif key == "menu_records":
            mode = input(t("ask_records") + ": ").strip()
            line = {"1": "record", "2": "chart records", "3": "chart plays"}.get(mode)
        elif key == "menu_repeat":
            from .repeat import OPPONENTS

            text = input(t("ask_game") + ": ").strip()
            rounds = input(t("ask_rounds") + " [10]: ").strip() or "10"
            bot = input(t("pick_bot") + " (" + ", ".join(OPPONENTS) + "): ").strip().lower()
            line = f"repeat {quote(text)} --rounds {rounds} --opponent {bot} --log" if text and bot else None
        elif key == "menu_claude":
            text = input(t("ask_claude_question") + ": ").strip()
            line = f"claude ask {quote(text)}" if text else "claude status"
        elif key == "menu_theme":
            name = input(t("pick_theme") + " (" + ", ".join(THEME_DETAILS) + "): ").strip().lower()
            line = f"theme {name}" if name else None
        if line is None:
            print(red("  Nothing to run. Choose again."))
            continue
        try:
            session.command(line)
        except SystemExit:
            continue
        except (ValueError, OSError) as exc:
            print(red("✗ " + str(exc)))


def run_menu_program(games):
    """Start the program on the menu: the default in a terminal, and 'playbook menu'.

    The menu's Command prompt entry, or Esc at the menu, goes to the prompt. Quit leaves the program.
    """
    global EDITOR
    from .catalog import playbook_home

    session = Session(games)
    EDITOR = lineedit.Editor(history_path=playbook_home() / "history", complete=_completer(games),
                             complete_phrase=_phrase_completer(games))
    try:
        if run_menu(session, back_quits=True):
            return 0
        print_banner()
        return _loop(session, games)
    finally:
        try:
            EDITOR.save_history()
        except OSError:
            pass


def run_launch(games):
    """What 'playbook' with no arguments does: the name, then the menu in a terminal, the prompt when input is piped."""
    if lineedit.is_terminal():
        if not lineedit.splash(box(app_box_lines(), border=green) + "\n"):
            return 0
        return run_menu_program(games)
    return run(games)
