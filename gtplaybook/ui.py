"""Terminal styling: themes, colour roles, bold headings, and boxes.

Colour is used only when stdout is a terminal and NO_COLOR is not set, so piped or
redirected output stays plain text.

Four roles carry the colour: accent (headings and borders), good (victory), bad (failure)
and mid (draw). A theme sets all four. You can change any role, and the choice is saved in
theme.json in the playbook home folder, so it survives restarts.
"""

import json
import os
import re
import sys
from pathlib import Path

RESET = "\x1b[0m"
_SGR = re.compile(r"\x1b\[[0-9;]*m")
ROLES = ("accent", "good", "bad", "mid")

# Each role is a 256-colour number, or None for no colour (bold still applies to headings).
THEMES = {
    "classic": {"accent": 208, "good": 34, "bad": 160, "mid": 245},
    "ocean": {"accent": 39, "good": 43, "bad": 203, "mid": 111},
    "forest": {"accent": 70, "good": 76, "bad": 166, "mid": 143},
    "contrast": {"accent": 226, "good": 46, "bad": 196, "mid": 255},
    "sunset": {"accent": 209, "good": 220, "bad": 161, "mid": 180},
    "midnight": {"accent": 105, "good": 117, "bad": 210, "mid": 146},
    "rose": {"accent": 204, "good": 151, "bad": 124, "mid": 250},
    "matrix": {"accent": 46, "good": 40, "bad": 196, "mid": 22},
    "paper": {"accent": 94, "good": 64, "bad": 124, "mid": 137},
    "claude-dark": {"accent": 173, "good": 114, "bad": 167, "mid": 246},
    "claude-light": {"accent": 166, "good": 28, "bad": 160, "mid": 241},
    "plain": {"accent": 250, "good": 252, "bad": 250, "mid": 245},
    "mono": {"accent": None, "good": None, "bad": None, "mid": None},
}

COLOUR_NAMES = {
    "black": 16, "grey": 245, "white": 255, "red": 196, "green": 46, "yellow": 226,
    "blue": 33, "magenta": 201, "cyan": 51, "orange": 208, "purple": 135, "none": None,
}

_active = dict(THEMES["classic"])
_theme_name = "classic"


def theme_file(home):
    return Path(home) / "theme.json"


def parse_colour(text):
    """A colour name (red, cyan, orange, ...), or a number from 0 to 255."""
    key = text.strip().lower()
    if key in COLOUR_NAMES:
        return COLOUR_NAMES[key]
    if key.isdigit() and 0 <= int(key) <= 255:
        return int(key)
    raise ValueError(f"'{text}' is not a colour. Use a name such as red or cyan, or a number from 0 to 255.")


def load_theme(home):
    """Apply the saved theme. A missing or unreadable file keeps the classic theme."""
    global _theme_name
    try:
        data = json.loads(theme_file(home).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    name = data.get("name", "classic")
    if name not in THEMES:
        name = "classic"
    _theme_name = name
    _active.update(THEMES[name])
    for role, value in (data.get("colors") or {}).items():
        if role in ROLES and (value is None or (isinstance(value, int) and 0 <= value <= 255)):
            _active[role] = value


def save_theme(home, name=None, colours=None):
    """Save a theme name, and any colour overrides, to theme.json."""
    data = {}
    try:
        data = json.loads(theme_file(home).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pass
    if name is not None:
        data = {"name": name, "colors": {}}
    if colours:
        data.setdefault("name", "classic")
        data.setdefault("colors", {}).update(colours)
    Path(home).mkdir(parents=True, exist_ok=True)
    theme_file(home).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    load_theme(home)


def reset_theme(home):
    try:
        theme_file(home).unlink()
    except FileNotFoundError:
        pass
    global _theme_name
    _theme_name = "classic"
    _active.clear()
    _active.update(THEMES["classic"])


_STANDARD_HEX = ["#000000", "#800000", "#008000", "#808000", "#000080", "#800080", "#008080", "#c0c0c0",
                 "#808080", "#ff0000", "#00ff00", "#ffff00", "#0000ff", "#ff00ff", "#00ffff", "#ffffff"]


def xterm_hex(n):
    """The hex colour of a 256-colour number, for charts."""
    if n < 16:
        return _STANDARD_HEX[n]
    if n >= 232:
        level = 8 + 10 * (n - 232)
        return f"#{level:02x}{level:02x}{level:02x}"
    index = n - 16
    steps = [0, 95, 135, 175, 215, 255]
    return "#" + "".join(f"{steps[part]:02x}" for part in (index // 36, (index // 6) % 6, index % 6))


def hex_for(role, fallback):
    """The hex colour for a role in the current theme; the fallback when the theme has no colour."""
    value = _active[role]
    return fallback if value is None else xterm_hex(value)


def current_theme():
    return _theme_name


def colour_enabled():
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def _sgr(value):
    return "" if value is None else f"\x1b[38;5;{value}m"


def _style(code, text):
    if not text or not colour_enabled() or not code:
        return text
    return f"{code}{text}{RESET}"


def plain(text):
    return text


def bold(text):
    return _style("\x1b[1m", text)


def dim(text):
    return _style("\x1b[2m", text)


def good(text):
    return _style(_sgr(_active["good"]), text)


def bad(text):
    return _style(_sgr(_active["bad"]), text)


def mid(text):
    return _style(_sgr(_active["mid"]), text)


def green(text):
    return good(text)


def red(text):
    return bad(text)


def accent(text):
    return _style(_sgr(_active["accent"]), text)


def heading(text):
    """The section title used throughout the session, in the accent colour."""
    return _style("\x1b[1m" + _sgr(_active["accent"]), "▸ " + text)


def cell(text, width, styler=plain):
    """Pad plain text to a column width, then style it, so ANSI codes do not break alignment."""
    return styler(text) + " " * max(0, width - len(text))


def visible_width(text):
    """The number of columns text takes on screen, not counting colour codes."""
    return len(_SGR.sub("", text))


def box(lines, border=None):
    """Draw text inside a rounded border. The border is styled; lines may carry their own colour.

    The plain theme draws the border with ASCII characters, for old terminals and fonts.
    """
    border = border or accent
    if _theme_name == "plain":
        tl, tr, bl, br, horiz, side = "+", "+", "+", "+", "-", "|"
    else:
        tl, tr, bl, br, horiz, side = "╭", "╮", "╰", "╯", "─", "│"
    inner = max(visible_width(line) for line in lines)
    out = [border(tl + horiz * (inner + 2) + tr)]
    for line in lines:
        out.append(border(side) + " " + line + " " * (inner - visible_width(line)) + " " + border(side))
    out.append(border(bl + horiz * (inner + 2) + br))
    return "\n".join(out)


def highlight_code():
    """The colour of the highlighted menu item: the accent colour, or none when colour is off."""
    return _sgr(_active["accent"]) if colour_enabled() else ""


def mid_code():
    """The colour of the detail line under a menu: the draw colour, or none when colour is off."""
    return _sgr(_active["mid"]) if colour_enabled() else ""
