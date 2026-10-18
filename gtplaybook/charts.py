"""SVG charts, maps and decision trees, with no external dependencies.

Charts:
  families  games per family, as bars
  traits    every game against every trait, as a heat-map
  map       the families and their sub-domains, as a radial map
  sim       the decision tree of one simulation, with the victory and failure paths marked
  records   your logged wins, losses and draws per game
"""

import math
from html import escape as _html_escape


def escape(text):
    """Escape text for SVG. Apostrophes are written as &#39;, as the Go version does."""
    return _html_escape(str(text)).replace("&#x27;", "&#39;")

from .catalog import TRAITS
from .sim import solve

PALETTE = ["#d97706", "#2563eb", "#059669", "#7c3aed", "#db2777", "#0891b2", "#65a30d", "#dc2626", "#4b5563"]
TRAIT_COLOURS = ["#2563eb", "#f59e0b", "#10b981", "#8b5cf6", "#ef4444", "#14b8a6"]


def _doc(width, height, title, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="-apple-system, Helvetica, Arial, sans-serif">'
        f"<title>{escape(title)}</title><rect width=\"100%\" height=\"100%\" fill=\"#ffffff\"/>"
        + "".join(body)
        + "</svg>\n"
    )


def families_chart(areas):
    rows = []
    for fam in areas:
        games = {g for sd in fam["subdomains"] for g in sd["games"]}
        rows.append((fam["family"], len(games)))
    rows.sort(key=lambda r: -r[1])
    width, left = 820, 300
    height = 60 + len(rows) * 26
    top_n = max(n for _, n in rows) or 1
    body = ['<text x="20" y="28" font-size="16" font-weight="600">Games per family</text>']
    for i, (name, n) in enumerate(rows):
        y = 44 + i * 26
        w = (width - left - 90) * n / top_n
        body.append(f'<text x="{left - 8}" y="{y + 13}" font-size="12" text-anchor="end">{escape(name)}</text>')
        body.append(f'<rect x="{left}" y="{y}" width="{w:.1f}" height="18" rx="3" fill="{PALETTE[i % len(PALETTE)]}"/>')
        body.append(f'<text x="{_num(left + w + 6)}" y="{y + 13}" font-size="12">{n}</text>')
    return _doc(width, height, "Games per family", body)


def traits_heatmap(games):
    cell_w, cell_h, left, top = 96, 11, 220, 60
    width = left + cell_w * len(TRAITS) + 20
    height = top + cell_h * len(games) + 30
    body = ['<text x="20" y="28" font-size="16" font-weight="600">Games by trait</text>']
    for c, key in enumerate(TRAITS):
        body.append(f'<text x="{_num(left + c * cell_w + cell_w / 2)}" y="{top - 10}" font-size="11" text-anchor="middle">{key}</text>')
    for r, game in enumerate(games):
        y = top + r * cell_h
        body.append(f'<text x="{left - 6}" y="{y + cell_h - 2}" font-size="8" text-anchor="end">{escape(game["name"][:34])}</text>')
        for c, key in enumerate(TRAITS):
            value = game["traits"].get(key)
            if value is None:
                continue
            colour = TRAIT_COLOURS[TRAITS[key].index(value) % len(TRAIT_COLOURS)]
            body.append(
                f'<rect x="{left + c * cell_w}" y="{y}" width="{cell_w - 2}" height="{cell_h - 1}" fill="{colour}">'
                f"<title>{escape(game['name'])}: {key} = {value}</title></rect>"
            )
    legend_y = height - 14
    body.append(f'<text x="{left}" y="{legend_y}" font-size="10" fill="#6b7280">Colours follow each trait\'s value order; hover a cell for its value.</text>')
    return _doc(width, height, "Games by trait", body)


def _wrap(text, width=14):
    words, lines, line = text.split(), [], ""
    for word in words:
        if line and len(line) + 1 + len(word) > width:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        lines.append(line)
    return lines[:3]


def family_map(areas):
    size = 1200
    cx = cy = size / 2
    body = [f'<text x="20" y="28" font-size="16" font-weight="600">Map of families and sub-domains</text>']
    n = len(areas)
    family_r, sub_r = 300, 470
    spokes = []
    for i, fam in enumerate(areas):
        angle = 2 * math.pi * i / n - math.pi / 2
        fx, fy = cx + family_r * math.cos(angle), cy + family_r * math.sin(angle)
        colour = PALETTE[i % len(PALETTE)]
        spokes.append(f'<line x1="{cx}" y1="{cy}" x2="{fx:.1f}" y2="{fy:.1f}" stroke="{colour}" stroke-width="2"/>')
        count = len({g for sd in fam["subdomains"] for g in sd["games"]})
        body.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="48" fill="{colour}"/>')
        lines = _wrap(fam["family"])
        top = fy - (len(lines) + 1) * 6
        for k, line in enumerate(lines):
            body.append(f'<text x="{fx:.1f}" y="{top + k * 12 + 10:.1f}" font-size="10" fill="#ffffff" text-anchor="middle">{escape(line)}</text>')
        body.append(f'<text x="{fx:.1f}" y="{top + len(lines) * 12 + 14:.1f}" font-size="10" fill="#ffffff" text-anchor="middle">{count} games</text>')
        subs = fam["subdomains"]
        spread = math.radians(40)
        for j, sd in enumerate(subs):
            frac = 0.5 if len(subs) == 1 else j / (len(subs) - 1)
            sangle = angle - spread / 2 + spread * frac
            sx, sy = cx + sub_r * math.cos(sangle), cy + sub_r * math.sin(sangle)
            spokes.append(f'<line x1="{fx:.1f}" y1="{fy:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" stroke="{colour}" stroke-opacity="0.5"/>')
            anchor = "start" if math.cos(sangle) >= 0 else "end"
            label = f"{sd['name']} ({len(sd['games'])})"
            body.append(f'<text x="{_num(sx)}" y="{_num(sy)}" font-size="9" fill="#374151" text-anchor="{anchor}">{escape(label)}</text>')
    centre = [f'<circle cx="{_num(cx)}" cy="{_num(cy)}" r="82" fill="#111827"/>']
    for k, line in enumerate(["Game theory", "playbook"]):
        centre.append(f'<text x="{_num(cx)}" y="{_num(cy - 4 + k * 16)}" font-size="13" fill="#ffffff" text-anchor="middle">{escape(line)}</text>')
    return _doc(size, size, "Map of families and sub-domains", spokes + body + centre)


def outcome_colours():
    """Win, loss, draw and mixed colours from the current theme, with light tints for fills."""
    from .ui import hex_for

    win, loss = hex_for("good", "#16a34a"), hex_for("bad", "#dc2626")
    draw, mixed = hex_for("mid", "#9ca3af"), hex_for("accent", "#f59e0b")
    return {
        "win": win, "loss": loss, "draw": draw, "mixed": mixed,
        "win_light": _mix(win, "#ffffff", 0.6), "loss_light": _mix(loss, "#ffffff", 0.6),
        "draw_light": _mix(draw, "#ffffff", 0.7),
    }


def _num(value):
    """A coordinate as a whole number when it is one, so the SVG matches the Go version."""
    return str(int(value)) if float(value).is_integer() else f"{value:.1f}"


def _mix(a, b, t):
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    # Round halves up, as Go's math.Round does, so both versions draw the same colours.
    return "#" + "".join(f"{int(math.floor(x + (y - x) * t + 0.5)):02x}" for x, y in zip(ca, cb))


def _plan_nodes(sim, plan):
    """Node ids along a plan from the start, with chance resolved by the likeliest branch."""
    nodes = sim["nodes"]
    nid, seen = sim["start"], []
    while True:
        seen.append(nid)
        node = nodes[nid]
        if node["type"] == "end":
            return seen
        if node["type"] == "nature":
            nid = max(node["branches"], key=lambda b: b["p"])["next"]
        else:
            nid = node["options"][plan[nid][1]]["next"]


def taken_nodes(sim, steps):
    """The node ids a run passed through, following the labels of its steps."""
    nodes = sim["nodes"]
    nid = sim["start"]
    path = [nid]
    for step in steps:
        node = nodes[nid]
        if node["type"] == "nature":
            options = node["branches"]
        elif node["type"] == "player":
            options = node["options"]
        else:
            break
        match = next((o for o in options if o["label"] == step["label"]), None)
        if match is None:
            break
        nid = match["next"]
        path.append(nid)
    return path


def sim_tree(sim, taken=None):
    """The decision tree. If taken (the steps of a run) is given, your run is outlined in the accent colour."""
    from .ui import hex_for

    colours = outcome_colours()
    accent_hex = hex_for("accent", "#f59e0b")
    your_path = taken_nodes(sim, taken) if taken else []
    your_edges = set(zip(your_path, your_path[1:]))
    nodes = sim["nodes"]
    victory = solve(sim, "victory")
    failure = solve(sim, "failure")
    win_path = set(_plan_nodes(sim, victory))
    fail_path = set(_plan_nodes(sim, failure))

    depth = {sim["start"]: 0}
    order = [sim["start"]]
    queue = [sim["start"]]
    while queue:
        cur = queue.pop(0)
        children = []
        node = nodes[cur]
        if node["type"] == "nature":
            children = [b["next"] for b in node["branches"]]
        elif node["type"] == "player":
            children = [o["next"] for o in node["options"]]
        for child in children:
            if child not in depth:
                depth[child] = depth[cur] + 1
                order.append(child)
                queue.append(child)

    by_depth = {}
    for nid in order:
        by_depth.setdefault(depth[nid], []).append(nid)
    box_w, box_h, gap_x, gap_y = 210, 58, 160, 18
    tallest = max(len(v) for v in by_depth.values())
    width = 40 + (max(by_depth) + 1) * (box_w + gap_x)
    height = 120 + tallest * (box_h + gap_y)
    pos = {}
    for d, ids in by_depth.items():
        for i, nid in enumerate(ids):
            pos[nid] = (30 + d * (box_w + gap_x), 100 + i * (box_h + gap_y))

    body = [f'<text x="20" y="28" font-size="16" font-weight="600">{escape(sim["name"])}</text>',
            '<text x="20" y="44" font-size="11" fill="#6b7280">Green path: best route to victory. Red dashed: route most likely to fail. Box colour: chance of victory from that point.</text>']
    if your_path:
        body.append(f'<text x="20" y="60" font-size="11" fill="{accent_hex}">Orange outline: the run you played.</text>')
    edge_labels = []
    for nid in order:
        node = nodes[nid]
        children = []
        if node["type"] == "nature":
            children = [(b["next"], f"{b['label']} ({b['p']:.0%})") for b in node["branches"]]
        elif node["type"] == "player":
            children = [(o["next"], o["label"]) for o in node["options"]]
        x1, y1 = pos[nid]
        for child, label in children:
            x2, y2 = pos[child]
            on_win = nid in win_path and child in win_path
            on_fail = nid in fail_path and child in fail_path
            stroke = colours["win"] if on_win else colours["loss"] if on_fail else colours["draw"]
            dash = ' stroke-dasharray="6 4"' if on_fail and not on_win else ""
            width_px = 3 if (on_win or on_fail) else 1
            if (nid, child) in your_edges:
                stroke, dash, width_px = accent_hex, "", 4
            body.append(f'<line x1="{x1 + box_w}" y1="{y1 + box_h / 2}" x2="{x2}" y2="{y2 + box_h / 2}" stroke="{stroke}" stroke-width="{width_px}"{dash}/>')
            edge_labels.append(f'<text x="{(x1 + box_w + x2) / 2:.0f}" y="{(y1 + y2) / 2 + box_h / 2 - 3:.0f}" font-size="9" fill="#374151" text-anchor="middle" stroke="#ffffff" stroke-width="4" paint-order="stroke">{escape(label[:26])}</text>')
    for nid in order:
        node = nodes[nid]
        x, y = pos[nid]
        chance = victory[nid][0]
        fill = _mix(colours["loss_light"], colours["win_light"], chance)
        if node["type"] == "end":
            caption = node["outcome"].upper()
            fill = {"victory": colours["win_light"], "draw": colours["draw_light"], "failure": colours["loss_light"]}[node["outcome"]]
        elif node["type"] == "nature":
            caption = "Chance: " + node["prompt"][:24]
        else:
            caption = node["prompt"][:30]
        mine = nid in your_path
        outline, outline_w = (accent_hex, 2.5) if mine else ("#374151", 0.5)
        body.append(f'<rect x="{x}" y="{y}" width="{box_w}" height="{box_h}" rx="6" fill="{fill}" stroke="{outline}" stroke-width="{outline_w}"/>')
        body.append(f'<text x="{x + 8}" y="{y + 18}" font-size="10" fill="#111827">{escape(caption)}</text>')
        if node["type"] != "end":
            body.append(f'<text x="{x + 8}" y="{y + 34}" font-size="9" fill="#374151">victory from here: {chance:.0%}</text>')
    body.extend(edge_labels)
    return _doc(int(width), int(height), f"{sim['name']} decision tree", body)


def records_chart(counts, names):
    rows = sorted(counts.items(), key=lambda kv: -sum(kv[1].values()))
    width, left = 820, 300
    height = 60 + len(rows) * 28 + 20
    top_n = max((sum(row.values()) for _, row in rows), default=1) or 1
    body = ['<text x="20" y="28" font-size="16" font-weight="600">Your results by game</text>']
    colours = outcome_colours()
    for i, (game_id, row) in enumerate(rows):
        y = 44 + i * 28
        body.append(f'<text x="{left - 8}" y="{y + 13}" font-size="12" text-anchor="end">{escape(names.get(game_id, game_id))}</text>')
        x = left
        for result in ("win", "loss", "draw", "mixed"):
            n = row.get(result, 0)
            if not n:
                continue
            w = (width - left - 90) * n / top_n
            body.append(f'<rect x="{_num(x)}" y="{y}" width="{_num(w)}" height="18" fill="{colours[result]}"><title>{result}: {n}</title></rect>')
            x += w
    legend_y = 44 + len(rows) * 28 + 6
    body.append(f'<text x="{left}" y="{legend_y}" font-size="11" fill="#374151">win, loss, draw and mixed follow your theme (theme command)</text>')
    return _doc(width, height, "Your results by game", body)


def plays_chart(rows):
    """rows: [(label, {"win": n, "loss": n, ...})] - one bar per play you have logged."""
    width, left = 880, 360
    height = 60 + len(rows) * 26 + 20
    top_n = max((sum(c.values()) for _, c in rows), default=1) or 1
    body = ['<text x="20" y="28" font-size="16" font-weight="600">Your results by play</text>']
    colours = outcome_colours()
    for i, (label, counts) in enumerate(rows):
        y = 44 + i * 26
        body.append(f'<text x="{left - 8}" y="{y + 13}" font-size="11" text-anchor="end">{escape(label[:58])}</text>')
        x = left
        for result in ("win", "loss", "draw", "mixed"):
            n = counts.get(result, 0)
            if not n:
                continue
            w = (width - left - 90) * n / top_n
            body.append(f'<rect x="{_num(x)}" y="{y}" width="{_num(w)}" height="18" fill="{colours[result]}"><title>{result}: {n}</title></rect>')
            x += w
    body.append(f'<text x="{left}" y="{44 + len(rows) * 26 + 6}" font-size="11" fill="#374151">win, loss, draw and mixed follow your theme (theme command)</text>')
    return _doc(width, height, "Your results by play", body)
