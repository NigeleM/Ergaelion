"""A terminal line editor, a menu chooser and a pager, using only the standard library.

On a terminal the input is read one key at a time, so the arrow keys, history, Tab completion, the
command list that appears when you type '/', the arrow-key menu and the pager all work. Off a
terminal (pipes, files, Windows) plain lines are read and the menu asks for a typed number.
"""

import os
import re
import sys

from .ui import highlight_code, mid_code

MAX_SUGGESTIONS = 8
NOT_TERMINAL = -2
_ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")

try:
    import termios
    import tty

    _HAVE_TERMIOS = True
except ImportError:  # Windows
    _HAVE_TERMIOS = False


def is_terminal(fd=None):
    fd = sys.stdin.fileno() if fd is None else fd
    try:
        return _HAVE_TERMIOS and os.isatty(fd)
    except (OSError, ValueError):
        return False


def visible_width(text):
    return len(_ANSI.sub("", text))


def terminal_rows(fd=None):
    try:
        return os.get_terminal_size(sys.stdout.fileno()).lines
    except (OSError, ValueError):
        return 24


def terminal_columns(fd=None):
    try:
        return os.get_terminal_size(sys.stdout.fileno()).columns
    except (OSError, ValueError):
        return 80


class _Raw:
    """Switches the terminal to one key at a time, without echo, and restores it afterwards."""

    def __init__(self, fd):
        self.fd = fd
        self.saved = None

    def __enter__(self):
        self.saved = termios.tcgetattr(self.fd)
        tty.setcbreak(self.fd)
        return self

    def __exit__(self, *exc):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.saved)


def _hl():
    """The start of a highlighted item: the accent colour in reverse video."""
    return highlight_code() + "\x1b[7m"


def _mid():
    return mid_code()


def _read_key(fd):
    """Read one key. Returns the character, or an escape sequence such as '\\x1b[A' for arrow keys."""
    first = os.read(fd, 1)
    if not first:
        return None
    byte = first[0]
    if byte == 0x1B:
        seq = b""
        nxt = os.read(fd, 1)
        if nxt not in (b"[", b"O"):
            return "\x1b"
        seq += nxt
        while True:
            c = os.read(fd, 1)
            if not c:
                break
            seq += c
            if c.isalpha() or c == b"~":
                break
        return "\x1b" + seq.decode("ascii", "replace")
    length = 1
    if byte >= 0xF0:
        length = 4
    elif byte >= 0xE0:
        length = 3
    elif byte >= 0xC0:
        length = 2
    data = first + b"".join(os.read(fd, 1) for _ in range(length - 1))
    return data.decode("utf-8", "replace")


class Editor:
    """Reads lines with editing, history and completion. complete(prefix) returns candidate words."""

    def __init__(self, history_path=None, complete=None, complete_phrase=None):
        self.history = []
        self.history_path = history_path
        self.complete = complete
        self.complete_phrase = complete_phrase
        if history_path and os.path.exists(history_path):
            with open(history_path, encoding="utf-8") as handle:
                self.history = [line.rstrip("\n") for line in handle if line.strip()][-500:]

    def save_history(self):
        if self.history_path:
            os.makedirs(os.path.dirname(self.history_path) or ".", exist_ok=True)
            with open(self.history_path, "w", encoding="utf-8") as handle:
                handle.write("\n".join(self.history[-500:]) + "\n")

    def _list_for(self, buf):
        if not self.complete or not buf or buf[0] != "/" or " " in buf:
            return []
        return self.complete(buf)[:MAX_SUGGESTIONS]

    def read_line(self, prompt):
        """Returns (line, ok). ok is False at end of input."""
        if not is_terminal():
            try:
                sys.stdout.write(prompt)
                sys.stdout.flush()
                line = sys.stdin.readline()
            except (OSError, ValueError):
                return "", False
            if not line:
                return "", False
            return line.rstrip("\r\n"), True
        fd = sys.stdin.fileno()
        with _Raw(fd):
            return self._edit(fd, prompt)

    def _edit(self, fd, prompt):
        out = sys.stdout
        buf, pos = [], 0
        index = len(self.history)
        saved = ""
        selected = 0
        shown = 0

        def render():
            nonlocal shown
            items = self._list_for("".join(buf))
            out.write(f"\r\x1b[2K{prompt}{''.join(buf)}\x1b[J")
            for i, item in enumerate(items):
                out.write("\r\n" + (f"{_hl()} {item} \x1b[0m" if i == selected else f"  {item}"))
            if items:
                out.write(f"\x1b[{len(items)}A")
            shown = len(items)
            column = visible_width(prompt) + pos
            out.write(f"\r\x1b[{column}C" if column else "\r")
            out.flush()

        def clear_list():
            nonlocal shown
            if shown:
                out.write("\x1b[J")
                shown = 0

        render()
        while True:
            key = _read_key(fd)
            if key is None:
                clear_list()
                out.write("\r\n")
                return "", False
            items = self._list_for("".join(buf))
            if key in ("\r", "\n"):
                clear_list()
                out.write("\r\n")
                line = "".join(buf)
                if line.strip() and (not self.history or self.history[-1] != line):
                    self.history.append(line)
                return line, True
            if key == "\x03":
                clear_list()
                out.write("^C\r\n")
                return "", True
            if key == "\x04":
                if not buf:
                    clear_list()
                    out.write("\r\n")
                    return "", False
                if pos < len(buf):
                    del buf[pos]
            elif key in ("\x7f", "\x08"):
                if pos > 0:
                    del buf[pos - 1]
                    pos -= 1
            elif key == "\x01":
                pos = 0
            elif key == "\x05":
                pos = len(buf)
            elif key == "\x0b":
                del buf[pos:]
            elif key == "\x15":
                del buf[:pos]
                pos = 0
            elif key == "\t":
                if items:
                    buf = list(items[selected] + " ")
                    pos = len(buf)
                    selected = 0
                elif self.complete:
                    text = self._complete_word("".join(buf), pos)
                    if text is not None:
                        buf, pos = list(text[0]), text[1]
                        if len(text) > 2 and text[2]:
                            clear_list()
                            out.write("\r\n" + "   ".join(text[2]) + "\r\n")
            elif key == "\x1b[A" or key == "\x1bOA":
                if items:
                    selected = (selected - 1) % len(items)
                elif index > 0:
                    if index == len(self.history):
                        saved = "".join(buf)
                    index -= 1
                    buf, pos = list(self.history[index]), len(self.history[index])
            elif key == "\x1b[B" or key == "\x1bOB":
                if items:
                    selected = (selected + 1) % len(items)
                elif index < len(self.history):
                    index += 1
                    text = saved if index == len(self.history) else self.history[index]
                    buf, pos = list(text), len(text)
            elif key in ("\x1b[C", "\x1bOC"):
                pos = min(pos + 1, len(buf))
            elif key in ("\x1b[D", "\x1bOD"):
                pos = max(pos - 1, 0)
            elif key in ("\x1b[H", "\x1bOH", "\x1b[1~"):
                pos = 0
            elif key in ("\x1b[F", "\x1bOF", "\x1b[4~"):
                pos = len(buf)
            elif key == "\x1b[3~":
                if pos < len(buf):
                    del buf[pos]
            elif len(key) == 1 and key.isprintable():
                buf.insert(pos, key)
                pos += 1
                selected = 0
            render()

    def _complete_word(self, text, pos):
        """Complete the word ending at pos. Returns (text, cursor[, candidates to list]) or None."""
        if self.complete_phrase and pos == len(text) and text[:1] != "/":
            phrases = self.complete_phrase(text[:pos])
            if phrases:
                common = _common_prefix(phrases)
                if len(phrases) == 1:
                    return phrases[0], len(phrases[0])
                if len(common) > len(text[:pos]):
                    return common, len(common)
                return text, pos, phrases
        start = pos
        while start > 0 and text[start - 1] != " ":
            start -= 1
        prefix = text[start:pos]
        matches = self.complete(prefix)
        if not matches:
            return None
        replacement = matches[0] + " " if len(matches) == 1 else _common_prefix(matches)
        if len(replacement) <= len(prefix):
            return (text, pos, matches) if len(matches) > 1 else None
        new_text = text[:start] + replacement + text[pos:]
        return new_text, start + len(replacement)


def _common_prefix(words):
    prefix = words[0]
    for word in words[1:]:
        while not word.startswith(prefix):
            prefix = prefix[:-1]
    return prefix


def choose(title, items):
    """Show a numbered list; move with the arrow keys, Enter picks, a number jumps, q cancels.

    Returns the chosen index, -1 if cancelled, or NOT_TERMINAL when the input is not a terminal.
    """
    if not is_terminal():
        return NOT_TERMINAL
    fd = sys.stdin.fileno()
    out = sys.stdout
    selected = 0
    out.write(f"{title}\r\n")

    def draw(first):
        for i, item in enumerate(items):
            out.write("\r\x1b[2K")
            if i == selected:
                out.write(f"\x1b[1;7m > {i + 1}) {item} \x1b[0m\r\n")
            else:
                out.write(f"   {i + 1}) {item}\r\n")
        out.write("\r\x1b[2K\x1b[2m  up/down to move, Enter to choose, a number to jump, q to go back\x1b[0m")
        out.write(f"\x1b[{len(items)}A")
        out.flush()

    with _Raw(fd):
        draw(True)
        while True:
            key = _read_key(fd)
            if key is None:
                return -1
            if key in ("\r", "\n"):
                out.write("\r\x1b[J")
                return selected
            if key in ("q", "\x03", "\x1b"):
                out.write("\r\x1b[J")
                return -1
            if len(key) == 1 and key.isdigit() and 1 <= int(key) <= len(items):
                out.write("\r\x1b[J")
                return int(key) - 1
            if key in ("k", "\x1b[A", "\x1bOA"):
                selected = (selected - 1) % len(items)
            elif key in ("j", "\x1b[B", "\x1bOB"):
                selected = (selected + 1) % len(items)
            draw(False)


def page(text):
    """Show text one screen at a time. Arrow keys, Page Up/Down, Space, g and G move; q closes."""
    lines = text.rstrip("\n").split("\n")
    height = max(terminal_rows() - 2, 5)
    if not is_terminal() or len(lines) <= height:
        sys.stdout.write(text)
        return
    fd = sys.stdin.fileno()
    out = sys.stdout
    top, max_top = 0, len(lines) - height

    def draw():
        out.write("\x1b[H\x1b[J")
        for line in lines[top:top + height]:
            out.write(line + "\r\n")
        out.write(f"{_hl()} lines {top + 1}-{min(top + height, len(lines))} of {len(lines)}"
                  "  up/down, PgUp/PgDn, g/G, q to close \x1b[0m")
        out.flush()

    with _Raw(fd):
        out.write("\x1b[?1049h")
        try:
            draw()
            while True:
                key = _read_key(fd)
                if key is None or key in ("q", "\x03", "\r", "\n", "\x1b"):
                    return
                if key in ("k", "\x1b[A", "\x1bOA"):
                    top -= 1
                elif key in ("j", "\x1b[B", "\x1bOB"):
                    top += 1
                elif key == " ":
                    top += height
                elif key == "\x1b[5~":
                    top -= height
                elif key == "\x1b[6~":
                    top += height
                elif key == "g":
                    top = 0
                elif key == "G":
                    top = max_top
                top = min(max(top, 0), max_top)
                draw()
        finally:
            out.write("\x1b[?1049l")
            out.flush()


def pick(title, items, extra=None):
    """A full-screen list with a description of the highlighted item.

    items are (label, detail) pairs. Enter returns (index, ""), q or Escape returns (-1, ""), and a
    key in extra returns (index, key). Off a terminal it returns (NOT_TERMINAL, "").
    """
    if not items or not is_terminal():
        return NOT_TERMINAL, ""
    extra = extra or {}
    fd = sys.stdin.fileno()
    out = sys.stdout
    hint = "up/down move  PgUp/PgDn page  Enter open  q back"
    for key in sorted(extra):
        hint += f"  {key} {extra[key]}"
    selected, top = 0, 0

    def list_rows():
        return max(terminal_rows() - 9 - title.count("\n"), 3)

    def draw():
        nonlocal top
        rows = list_rows()
        if selected < top:
            top = selected
        if selected >= top + rows:
            top = selected - rows + 1
        buf = ["\x1b[H\x1b[J", title.replace("\n", "\r\n") + "\r\n\r\n"]
        for i in range(top, min(top + rows, len(items))):
            label = items[i][0]
            buf.append(f"{_hl()} > {label} \x1b[0m\r\n" if i == selected else f"   {label}\r\n")
        buf.append("\r\n")
        for line in _wrap_words(items[selected][1], 96, 4):
            buf.append(f"{_mid()}{line}\x1b[0m\r\n")
        buf.append(f"{_hl()} {selected + 1}/{len(items)}  {hint} \x1b[0m")
        out.write("".join(buf))
        out.flush()

    with _Raw(fd):
        out.write("\x1b[?1049h")
        try:
            draw()
            while True:
                key = _read_key(fd)
                if key is None or key in ("\r", "\n"):
                    return (selected, "") if key else (-1, "")
                if key in ("q", "\x03", "\x1b"):
                    return -1, ""
                if key in ("k", "\x1b[A", "\x1bOA"):
                    selected = (selected - 1) % len(items)
                elif key in ("j", "\x1b[B", "\x1bOB"):
                    selected = (selected + 1) % len(items)
                elif key == "g":
                    selected = 0
                elif key == "G":
                    selected = len(items) - 1
                elif key == "\x1b[5~":
                    selected = max(selected - list_rows(), 0)
                elif key == "\x1b[6~":
                    selected = min(selected + list_rows(), len(items) - 1)
                elif key in extra:
                    return selected, key
                draw()
        finally:
            out.write("\x1b[?1049l")
            out.flush()


def splash(text):
    """Show text full screen until Enter or Space (returns True), or q (returns False).

    Off a terminal there is nothing to wait for, so it returns True.
    """
    if not is_terminal():
        return True
    fd = sys.stdin.fileno()
    out = sys.stdout
    with _Raw(fd):
        out.write("\x1b[?1049h\x1b[H\x1b[J" + text.replace("\n", "\r\n") + "\r\n"
                  + f"{_hl()} Press Enter or Space to continue   q quit \x1b[0m")
        out.flush()
        try:
            while True:
                key = _read_key(fd)
                if key is None or key in ("\r", "\n", " "):
                    return True
                if key in ("q", "\x03"):
                    return False
        finally:
            out.write("\x1b[?1049l")
            out.flush()


def view(text):
    """Show text full screen, scrollable, until q or Escape. Always full screen, even if it fits."""
    if not is_terminal():
        sys.stdout.write(text)
        return
    lines = text.rstrip("\n").split("\n")
    height = max(terminal_rows() - 2, 5)
    fd = sys.stdin.fileno()
    out = sys.stdout
    top, max_top = 0, max(len(lines) - height, 0)

    def draw():
        out.write("\x1b[H\x1b[J")
        for line in lines[top:top + height]:
            out.write(line + "\r\n")
        out.write(f"{_hl()} lines {top + 1}-{min(top + height, len(lines))} of {len(lines)}"
                  "  up/down, PgUp/PgDn, g/G, q to close \x1b[0m")
        out.flush()

    with _Raw(fd):
        out.write("\x1b[?1049h")
        try:
            draw()
            while True:
                key = _read_key(fd)
                if key is None or key in ("q", "\x03", "\r", "\n", "\x1b"):
                    return
                if key in ("k", "\x1b[A", "\x1bOA"):
                    top -= 1
                elif key in ("j", "\x1b[B", "\x1bOB"):
                    top += 1
                elif key == " ":
                    top += height
                elif key == "\x1b[5~":
                    top -= height
                elif key == "\x1b[6~":
                    top += height
                elif key == "g":
                    top = 0
                elif key == "G":
                    top = max_top
                top = min(max(top, 0), max_top)
                draw()
        finally:
            out.write("\x1b[?1049l")
            out.flush()


def _wrap_words(text, width, max_lines):
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > width:
            lines.append(line)
            line = word
            if len(lines) == max_lines:
                return lines
        else:
            line = f"{line} {word}".strip()
    if line and len(lines) < max_lines:
        lines.append(line)
    return lines
