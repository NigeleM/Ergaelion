"""Keyword parser: find the games, families and simulations a description points to.

Someone describes a situation in a few words, such as "work, strategy" or "price war". The parser
finds the phrases it knows (data/keywords.json) and ranks the games that use them. The answer is a
suggestion, not a verdict, so the playbook asks whether it fits and invites more words.
"""

import json
import re
from pathlib import Path

from .catalog import DATA_DIR, load_areas
from .sim import load_simulations

KEYWORD_FILE = "keywords.json"


def load_keywords(data_dir=DATA_DIR):
    return json.loads((Path(data_dir) / KEYWORD_FILE).read_text(encoding="utf-8"))


def _tokens(text):
    return re.findall(r"[a-z]+", text.lower().replace("'", ""))


def _same_word(a, b):
    """Words match if equal, or one is the other with a plural 's' (or 'es')."""
    if a == b:
        return True
    return a + "s" == b or b + "s" == a or a + "es" == b or b + "es" == a


def phrase_matches(text_tokens, phrase):
    """True if every word of the phrase appears in order in the text (plurals allowed)."""
    words = _tokens(phrase)
    if not words:
        return False
    for start in range(len(text_tokens) - len(words) + 1):
        if all(_same_word(text_tokens[start + i], words[i]) for i in range(len(words))):
            return True
    return False


def matched_phrases(text, phrases):
    tokens = _tokens(text)
    return [phrase for phrase in phrases if phrase_matches(tokens, phrase)]


def suggest(text, games, sims=None, keywords=None, top=5):
    """Rank games, families and simulations by the phrases a description matches.

    Returns a dict with the matched phrases and the top results of each kind, best first.
    """
    keywords = keywords or load_keywords()
    sims = sims if sims is not None else load_simulations()
    areas = load_areas()
    family_of_game = {}
    for area in areas:
        for sub in area["subdomains"]:
            for gid in sub["games"]:
                family_of_game.setdefault(gid, set()).add(area["family"])

    family_hits = {}
    for family, words in keywords["families"].items():
        found = matched_phrases(text, words)
        if found:
            family_hits[family] = found

    game_hits = {}
    for game in games:
        found = matched_phrases(text, keywords["games"].get(game["id"], []))
        if found:
            game_hits[game["id"]] = found

    def weight(gid):
        # A longer matched phrase is stronger evidence than a single word.
        return sum(len(_tokens(phrase)) for phrase in game_hits[gid])

    ranked_games = sorted(game_hits, key=lambda gid: (-weight(gid), gid))
    game_names = {g["id"]: g["name"] for g in games}
    family_scores = {}
    for family in family_hits:
        family_scores[family] = len(family_hits[family])
    for gid in game_hits:
        for family in family_of_game.get(gid, ()):
            family_scores[family] = family_scores.get(family, 0) + 1

    ranked_families = sorted(family_scores, key=lambda f: (-family_scores[f], f))
    sim_hits = []
    for sim in sims:
        score = sum(1 for f in sim["families"] if f in family_scores)
        if score:
            sim_hits.append((score, sim["id"], sim["name"]))
    sim_hits.sort(key=lambda row: (-row[0], row[1]))

    games_out = [(gid, game_names[gid], game_hits[gid]) for gid in ranked_games[:top]]
    if not games_out and ranked_families:
        # No game phrase matched, so offer the games in the best-matching area, labelled as area matches.
        in_area = sorted(gid for gid, fams in family_of_game.items() if ranked_families[0] in fams)
        games_out = [(gid, game_names[gid], [f"in {ranked_families[0]}"]) for gid in in_area[:top]]

    return {
        "phrases": sorted({phrase for found in family_hits.values() for phrase in found} |
                          {phrase for found in game_hits.values() for phrase in found}),
        "games": games_out,
        "families": [(family, family_scores[family]) for family in ranked_families[:top]],
        "simulations": [(sid, name) for _, sid, name in sim_hits[:top]],
    }


def describe(result, text):
    """The suggestion as lines of text, ending with a question about whether it fits."""
    if not result["games"] and not result["families"]:
        return [f"Nothing in '{text}' matched a known game, family or phrase.",
                "Try a few more words, such as a situation (price war, bank run), a role (boss, voter, rebel)"
                " or a kind of game (bluff, bargain, shared resource)."]
    lines = []
    if result["phrases"]:
        lines.append("Based on these words (" + ", ".join(result["phrases"]) + ") it looks like you're looking for:")
    else:
        lines.append("Based on your words it looks like you're looking for:")
    if result["games"]:
        lines.append("Games:")
        for _, name, found in result["games"]:
            lines.append(f"  - {name}  (matched: {', '.join(found)})")
    if result["families"]:
        lines.append("Areas: " + ", ".join(family for family, _ in result["families"]))
    if result["simulations"]:
        lines.append("Simulations: " + ", ".join(name for _, name in result["simulations"]))
    lines.append("Does this fit? If not, add or change words, for example 'price war with a new competitor'.")
    return lines


def vocabulary(games, keyword_data=None, combinations=None):
    """Every word a description is likely to use: words from the game phrases, area words, combination
    phrases and game names. Sorted, so the session can complete a partly typed word."""
    keyword_data = keyword_data or load_keywords()
    words = set()
    for phrases in keyword_data["games"].values():
        for phrase in phrases:
            words.update(_tokens(phrase))
    for phrases in keyword_data["families"].values():
        for phrase in phrases:
            words.update(_tokens(phrase))
    for combo in combinations or []:
        for phrase in combo["phrases"]:
            words.update(_tokens(phrase))
    for game in games:
        words.update(_tokens(game["name"]))
    return sorted(w for w in words if len(w) > 2)


def phrase_list(keyword_data, combinations=None):
    """Every known scenario phrase, lower case and sorted, for completing a whole phrase."""
    phrases = set()
    for items in keyword_data["games"].values():
        phrases.update(p.lower() for p in items)
    for combo in combinations or []:
        phrases.update(p.lower() for p in combo["phrases"])
    return sorted(phrases)


def complete_phrase(text, phrases, limit=12):
    """Known phrases that continue the text. Needs at least two words, so single words use complete_word."""
    typed = text.lower().lstrip()
    if " " not in typed.strip() or len(typed) < 8:
        return []
    matches = [p for p in phrases if p.startswith(typed) and p != typed]
    return sorted(matches, key=lambda p: (len(p), p))[:limit]


def complete_word(prefix, vocabulary_words, limit=12):
    """Vocabulary words that start with the prefix, shortest first, so the most direct completions lead."""
    prefix = prefix.lower()
    matches = [w for w in vocabulary_words if w.startswith(prefix) and w != prefix]
    return sorted(matches, key=lambda w: (len(w), w))[:limit]


def edit_distance(a, b):
    """Number of single-letter insertions, deletions and substitutions that turn a into b."""
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (ca != cb)))
        previous = current
    return previous[-1]


def close_words(text, vocabulary_words, limit=3):
    """For each word in the text the vocabulary does not know, the nearest known words (a likely typo).

    Returns (word, [suggestions]) pairs for words that have at least one close match.
    """
    known = set(vocabulary_words)
    out = []
    for word in sorted(set(_tokens(text))):
        if len(word) < 4 or word in known:
            continue
        allowed = 1 if len(word) <= 5 else 2
        near = sorted((edit_distance(word, v), v) for v in vocabulary_words if abs(len(v) - len(word)) <= allowed)
        suggestions = [v for dist, v in near if dist <= allowed][:limit]
        if suggestions:
            out.append((word, suggestions))
    return out


def correct_text(text, vocabulary_words):
    """Replace a likely typo with the one known word that is closest to it, when that match is unambiguous.

    Only a one-letter substitution is corrected (the same length, one letter different), in words of six
    letters or more, and only where exactly one known word matches that way. Insertions and deletions are
    left alone, because "border" and "order" are both real words. Returns (corrected text, [(from, to), ...]).
    """
    known = set(vocabulary_words)
    changes = []
    out = text
    for word in sorted(set(_tokens(text))):
        if len(word) < 6 or word in known:
            continue
        near = [v for v in vocabulary_words if len(v) == len(word) and edit_distance(word, v) == 1]
        if len(near) == 1:
            pattern = re.compile(r"\b" + re.escape(word) + r"\b", re.IGNORECASE)
            out = pattern.sub(near[0], out)
            changes.append((word, near[0]))
    return out, changes
