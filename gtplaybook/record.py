"""Win and loss records for games, kept in the playbook home folder.

Each outcome is one line of JSON in outcomes.jsonl, so records are easy to back up,
read by other tools, and never overwrite earlier entries.
"""

import json
import time
from pathlib import Path

from .catalog import playbook_home

RESULTS = ("win", "loss", "draw", "mixed")


def _file(home=None):
    return Path(home or playbook_home()) / "outcomes.jsonl"


def log_outcome(game_id, result, note="", home=None, play=None):
    if result not in RESULTS:
        raise ValueError(f"result must be one of {', '.join(RESULTS)}")
    path = _file(home)
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"game": game_id, "result": result, "note": note, "date": time.strftime("%Y-%m-%d")}
    if play is not None:
        entry["play"] = play
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def history(game_id=None, home=None):
    """Return logged entries, oldest first, optionally for one game."""
    path = _file(home)
    if not path.exists():
        return []
    entries = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if game_id:
        entries = [e for e in entries if e["game"] == game_id]
    return entries


def tally(home=None):
    """Return {game_id: {"win": n, "loss": n, "draw": n, "mixed": n}}."""
    counts = {}
    for entry in history(home=home):
        row = counts.setdefault(entry["game"], {result: 0 for result in RESULTS})
        row[entry["result"]] += 1
    return counts


def format_record(counts):
    return f"{counts['win']}W {counts['loss']}L {counts['draw']}D {counts['mixed']}M"


def remove_last(game_id=None, home=None):
    """Delete the most recent logged result (for one game if given). Returns it, or None."""
    path = _file(home)
    if not path.exists():
        return None
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for index in range(len(lines) - 1, -1, -1):
        entry = json.loads(lines[index])
        if game_id is None or entry["game"] == game_id:
            del lines[index]
            path.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")
            return entry
    return None


def to_csv(home=None):
    rows = ["date,game,result,play,note"]
    for entry in history(home=home):
        note = entry.get("note", "").replace('"', '""')
        rows.append(f'{entry["date"]},{entry["game"]},{entry["result"]},{entry.get("play", "")},"{note}"')
    return "\n".join(rows) + "\n"
