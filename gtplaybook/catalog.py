"""Loads the game catalogue and the family map, with optional user overlays.

Built-in games live in data/*.json. A user can change or extend them without
rebuilding: any file in <playbook home>/games/ holds one whole game. If its id
matches a built-in game it replaces it; otherwise it adds a new game. The family
map can be replaced the same way with <playbook home>/areas.json.

The playbook home is $PLAYBOOK_HOME if set, otherwise ~/.playbook.
"""

import json
import re
import os
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
AREAS_FILE = "areas.json"
NON_GAME_FILES = (AREAS_FILE, "simulations.json", "problems.json", "setup-help.json", "guide.json", "keywords.json", "tools.json", "help.txt", "combinations.json", "engine-games.json")

# Every trait a scenario or game can declare, and its allowed values.
TRAITS = {
    "players": ("two", "many"),
    "timing": ("simultaneous", "sequential"),
    "interaction": ("one-shot", "repeated"),
    "information": ("perfect", "imperfect"),
    "payoff": ("zero-sum", "mixed", "common-interest"),
    "communication": ("yes", "no"),
    "enforcement": ("yes", "no"),
    "commitment": ("yes", "no"),
    "bargaining": ("yes", "no"),
}

REQUIRED_FIELDS = ("id", "name", "category", "summary", "how_it_works", "traits", "domains", "strategies")


class CatalogError(ValueError):
    pass


def playbook_home():
    configured = os.environ.get("PLAYBOOK_HOME")
    return Path(configured) if configured else Path.home() / ".playbook"


def disabled_ids(home=None):
    """Game ids you have switched off. They stay in the data files but are hidden from the playbook."""
    path = Path(home or playbook_home()) / "disabled.txt"
    if not path.exists():
        return set()
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def set_disabled(game_id, disabled, home=None):
    folder = Path(home or playbook_home())
    folder.mkdir(parents=True, exist_ok=True)
    current = disabled_ids(home)
    current.discard(game_id)
    if disabled:
        current.add(game_id)
    (folder / "disabled.txt").write_text("".join(f"{item}\n" for item in sorted(current)), encoding="utf-8")


def check_overlays(home=None):
    """Return a list of problems found in your overlay files (empty when all are valid)."""
    problems = []
    folder = Path(home or playbook_home()) / "games"
    seen = set()
    if folder.is_dir():
        for path in sorted(folder.glob("*.json")):
            try:
                game = json.loads(path.read_text(encoding="utf-8"))
                _validate(game, seen)
            except (ValueError, KeyError, TypeError) as exc:
                problems.append(f"{path.name}: {exc}")
    areas = Path(home or playbook_home()) / AREAS_FILE
    if areas.exists():
        try:
            json.loads(areas.read_text(encoding="utf-8"))
        except ValueError as exc:
            problems.append(f"{AREAS_FILE}: {exc}")
    return problems


def load_games(data_dir=DATA_DIR, home=None):
    games = []
    for path in sorted(Path(data_dir).glob("*.json")):
        if path.name in NON_GAME_FILES:
            continue
        games.extend(json.loads(path.read_text(encoding="utf-8")))

    overlays = {}
    overlay_dir = Path(home or playbook_home()) / "games"
    if overlay_dir.is_dir():
        for path in sorted(overlay_dir.glob("*.json")):
            game = json.loads(path.read_text(encoding="utf-8"))
            overlays[game.get("id")] = game

    merged = [overlays.pop(game.get("id"), game) for game in games]
    merged.extend(overlays.values())
    hidden = disabled_ids(home)
    merged = [game for game in merged if game.get("id") not in hidden]

    seen = set()
    for game in merged:
        _validate(game, seen)
    return merged


def load_areas(data_dir=DATA_DIR, home=None):
    overlay = Path(home or playbook_home()) / AREAS_FILE
    path = overlay if overlay.exists() else Path(data_dir) / AREAS_FILE
    return json.loads(path.read_text(encoding="utf-8"))


def safe_name(text):
    """A name that is safe as a file name: letters, digits, dashes and underscores, and no dots."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,99}", text):
        raise ValueError(f"'{text}' cannot be used as a file name. Use letters, numbers, dashes and underscores.")
    return text


def save_overlay(game, home=None):
    """Write a whole game into the overlay folder so it can be edited by hand."""
    folder = Path(home or playbook_home()) / "games"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{safe_name(game['id'])}.json"
    path.write_text(json.dumps(game, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _validate(game, seen):
    missing = [field for field in REQUIRED_FIELDS if field not in game]
    if missing:
        raise CatalogError(f"{game.get('id', '?')}: missing fields {missing}")
    if game["id"] in seen:
        raise CatalogError(f"duplicate game id: {game['id']}")
    seen.add(game["id"])
    for key, value in game["traits"].items():
        if key not in TRAITS or value not in TRAITS[key]:
            raise CatalogError(f"{game['id']}: invalid trait {key}={value}")
    matrix = game.get("matrix")
    if matrix:
        rows, cols = len(matrix["rows"]), len(matrix["cols"])
        if len(matrix["payoffs"]) != rows or any(len(row) != cols for row in matrix["payoffs"]):
            raise CatalogError(f"{game['id']}: payoff matrix shape does not match its action names")


def find_game(games, query):
    needle = query.lower().strip()
    exact = [g for g in games if g["id"] == needle or g["name"].lower() == needle]
    if exact:
        return exact[0]
    partial = [g for g in games if needle in g["id"] or needle in g["name"].lower()]
    if len(partial) == 1:
        return partial[0]
    if not partial:
        raise CatalogError(f"no game matches '{query}'")
    raise CatalogError(f"'{query}' is ambiguous: " + ", ".join(g["id"] for g in partial))
