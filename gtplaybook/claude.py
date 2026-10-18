"""Optional Claude help inside the playbook.

Nothing here runs unless you switch it on with /claude on, and an API key is set in
ANTHROPIC_API_KEY. When it runs, it sends only what you asked about: your question,
and the text of the game, simulation or situation you are looking at. Nothing else
from your machine is sent. /claude status shows the current setting.
"""

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from .catalog import playbook_home

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"
DEFAULT_MODEL = "claude-sonnet-5-5"
MAX_TOKENS = 1024
MAX_PART = 6000
MAX_QUESTION = 2000
TIMEOUT_SECONDS = 60

SYSTEM = (
    "You help a person understand game theory with a playbook app. Use only the game, "
    "simulation or situation text given to you. Say plainly when that text does not "
    "answer the question. Explain the reasoning and the trade-offs. Do not give tactics "
    "for coercing, deceiving or harming specific people, and do not help with anything "
    "illegal. Keep the answer under 300 words."
)


def config_path(home=None):
    return Path(home or playbook_home()) / "claude.json"


def is_on(home=None):
    try:
        return bool(json.loads(config_path(home).read_text(encoding="utf-8")).get("consent"))
    except (OSError, ValueError):
        return False


def set_on(value, home=None):
    path = config_path(home)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"consent": bool(value)}) + "\n", encoding="utf-8")


def model():
    return os.environ.get("GTP_CLAUDE_MODEL") or DEFAULT_MODEL


def api_key():
    return os.environ.get("ANTHROPIC_API_KEY", "")


def clip(text, limit):
    text = text.strip()
    return text if len(text) <= limit else text[:limit].rstrip() + " …"


def game_part(game):
    """The text of one game, as Claude sees it."""
    lines = [game["name"], game["summary"]]
    if game.get("how_it_works"):
        lines.append("How it works: " + game["how_it_works"])
    matrix = game.get("matrix")
    if matrix and matrix.get("payoffs"):
        lines.append("Payoffs (row player, column player):")
        for label, row in zip(matrix["rows"], matrix["payoffs"]):
            cells = "  ".join(f"({cols[0]}, {cols[1]})" for cols in row)
            lines.append(f"  {label}: {cells}")
    for key, title in (("strategies", "Playbook"), ("pitfalls", "Pitfalls")):
        if game.get(key):
            lines.append(title + ":")
            lines.extend("  - " + item for item in game[key])
    return clip("\n".join(lines), MAX_PART)


def simulation_part(sim):
    """The text of one simulation: each decision, its options, and how it can end."""
    lines = [sim["name"], sim["summary"], "Decisions and outcomes:"]
    nodes = sim["nodes"]
    seen = set()
    queue = [sim["start"]]
    while queue:
        nid = queue.pop(0)
        if nid in seen or nid not in nodes:
            continue
        seen.add(nid)
        node = nodes[nid]
        if node["type"] == "end":
            lines.append(f"[{nid}] End: {node['outcome']}")
        elif node["type"] == "nature":
            branches = "; ".join(f"{round(b['p'] * 100)}% {b['label']} -> {b['next']}" for b in node["branches"])
            lines.append(f"[{nid}] Chance: {node['prompt']} {branches}")
            queue.extend(b["next"] for b in node["branches"])
        else:
            options = "; ".join(f"{o['label']} -> {o['next']}" for o in node["options"])
            lines.append(f"[{nid}] Decision: {node['prompt']} {options}")
            queue.extend(o["next"] for o in node["options"])
    return clip("\n".join(lines), MAX_PART)


def scenario_part(text, games_text):
    """The situation the person described, with the top matching games."""
    return clip("Situation: " + text.strip() + ("\n\n" + games_text if games_text else ""), MAX_PART)


def build_prompt(question, parts):
    """The user message: each (heading, text) part, then the question."""
    sections = [f"## {heading}\n{text}" for heading, text in parts if text]
    sections.append("## Question\n" + clip(question, MAX_QUESTION))
    return "\n\n".join(sections)


def build_request(question, parts):
    return {
        "model": model(),
        "max_tokens": MAX_TOKENS,
        "system": SYSTEM,
        "messages": [{"role": "user", "content": build_prompt(question, parts)}],
    }


def check_ready(home=None):
    """Raise ValueError with a plain message if Claude cannot be used yet."""
    if not is_on(home):
        raise ValueError("Claude is off. Type /claude on to allow questions to be sent to Anthropic.")
    if not api_key():
        raise ValueError("Set ANTHROPIC_API_KEY to use Claude. The rest of the playbook works without it.")


def send(payload, opener=urllib.request.urlopen):
    """POST the request and return the answer text."""
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "content-type": "application/json",
            "x-api-key": api_key(),
            "anthropic-version": API_VERSION,
        },
        method="POST",
    )
    try:
        with opener(request, timeout=TIMEOUT_SECONDS) as reply:
            data = json.loads(reply.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        code = exc.code
        exc.close()
        raise ValueError(f"Claude returned an error ({code}). Check the key and the model name.") from None
    except (urllib.error.URLError, OSError) as exc:
        raise ValueError(f"could not reach Anthropic: {exc}") from exc
    text = "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text")
    if not text:
        raise ValueError("Claude sent no text back")
    return text.strip()


def ask(question, parts, home=None, opener=urllib.request.urlopen):
    """Check consent and the key, then send the question. Returns (answer, characters_sent)."""
    check_ready(home)
    payload = build_request(question, parts)
    return send(payload, opener), len(payload["messages"][0]["content"])
