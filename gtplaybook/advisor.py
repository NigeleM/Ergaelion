"""Scores games against a scenario and produces general playbook rules.

A game's fit comes from three things: the phrases in the description that the game is known by
(keywords.json), the content words the description shares with the game's own text, and how well
the traits inferred from the description agree with the game's traits. Phrases count most, because
they were written for the way people describe these situations.
"""

import re

from . import keywords

PHRASE_POINTS = 3.0
WORD_POINTS = 1.0
TRAIT_POINTS = 0.5
DOMAIN_POINTS = 0.5

# Words that say nothing about which game fits. Kept short and general on purpose.
STOP_WORDS = set("""a an the and or but if then else of to in on at by for with from as is are was were be been
being it its this that these those i me my we our you your they their them he she his her there here what which
who whom whose do does did doing have has had having will would should could can cannot not no yes so than too
very just also about into over under up down out off again once only own same other each both all any some such
more most less least how when where why s t don't dont want wants need needs get gets make makes one two three
many much time times round decide decides people prefer prefers really think something things thing going goes
know knows different problem try tries trying keeps keep
""".split())

GENERAL_RULES = [
    (
        lambda t: t.get("interaction") == "repeated",
        "Repeated play: cooperation can last if the future matters enough. Never defect in a known final round, and make your moves easy to read.",
    ),
    (
        lambda t: t.get("interaction") == "one-shot" and t.get("payoff") == "mixed" and t.get("enforcement") != "yes",
        "One-shot, mixed payoffs, no enforcement: expect the other side to defect if it can. Change the structure (contracts, penalties, escrow) rather than relying on goodwill.",
    ),
    (
        lambda t: t.get("timing") == "sequential",
        "Sequential moves: reason backward from the end. Ask what you would do at your last decision, work back, and check whether each threat or promise is credible.",
    ),
    (
        lambda t: t.get("information") == "imperfect",
        "Hidden information: costly signals are believable and cheap talk is not. Screen the other side with choices they must make, and verify claims.",
    ),
    (
        lambda t: t.get("commitment") == "yes",
        "Commitment matters: a threat or promise only works if it is visible and hard to reverse. Make backing out costly.",
    ),
    (
        lambda t: t.get("payoff") == "zero-sum",
        "Zero-sum: assume a capable opponent. Play maximin (the best worst case), avoid predictable patterns, and randomise where needed.",
    ),
    (
        lambda t: t.get("players") == "many",
        "Many players: free-riding is the default. Make contributions visible and add sanctions that are credible and proportionate.",
    ),
    (
        lambda t: t.get("bargaining") == "yes",
        "Bargaining: know your outside option (BATNA) before you talk. The better your alternative, the bigger your share. Patience is leverage, so notice who is under more time pressure.",
    ),
    (
        lambda t: t.get("communication") == "yes" and t.get("payoff") != "zero-sum",
        "Communication: promises are cheap. Use talk to agree on a focal point, then confirm it with an action the other side can observe.",
    ),
]


def record_adjustment(counts):
    """Nudge a game's fit by your results: +0.5 per net win, capped at +/-2. Zero with no results."""
    if not counts:
        return 0.0
    net = counts.get("win", 0) - counts.get("loss", 0)
    return max(-2.0, min(2.0, 0.5 * net))


def content_words(text):
    """The distinct content words in a text, lower-case, with a simple plural ending removed."""
    out = set()
    for word in re.findall(r"[a-z]+", text.lower().replace("'", "")):
        if len(word) < 3 or word in STOP_WORDS:
            continue
        if len(word) > 4 and word.endswith("ies"):
            word = word[:-3] + "y"
        elif len(word) > 4 and word.endswith("s") and not word.endswith("ss"):
            word = word[:-1]
        out.add(word)
    return out


_GAME_WORDS = {}


def game_words(game):
    """The content words in a game's name, category, summary, how it works and examples. The name counts twice."""
    if game["id"] not in _GAME_WORDS:
        parts = [game["name"], game["name"], game["category"], game["summary"], game["how_it_works"]]
        parts += game.get("examples", [])
        _GAME_WORDS[game["id"]] = content_words(" ".join(parts))
    return _GAME_WORDS[game["id"]]


def rank_games(games, traits, domains, top=3, records=None, text="", keyword_data=None):
    """Score each game and return the best `top`, highest first.

    text is the description the traits came from (optional). keyword_data is the parsed keywords.json.
    records is {game_id: {"win": n, "loss": n, ...}} from your logged outcomes; it nudges the score.
    """
    records = records or {}
    phrases_by_game = (keyword_data or {}).get("games", {})
    tokens = keywords._tokens(text) if text else []
    described = content_words(text) if text else set()
    ranked = []
    for game in games:
        matched, clashed = [], []
        for key, value in traits.items():
            expected = game["traits"].get(key)
            if expected is None:
                continue
            (matched if expected == value else clashed).append(key)
        shared = sorted(set(domains) & set(game["domains"]))
        phrases = [p for p in phrases_by_game.get(game["id"], []) if keywords.phrase_matches(tokens, p)]
        words = sorted(described & game_words(game))
        adjustment = record_adjustment(records.get(game["id"]))
        score = (PHRASE_POINTS * len(phrases) + WORD_POINTS * len(words)
                 + TRAIT_POINTS * (len(matched) - len(clashed)) + DOMAIN_POINTS * len(shared) + adjustment)
        ranked.append({
            "game": game,
            "score": score,
            "record_adjustment": adjustment,
            "matched": matched,
            "clashed": clashed,
            "shared_domains": shared,
            "phrases": phrases,
            "words": words,
        })
    ranked.sort(key=lambda hit: (-hit["score"], hit["game"]["name"]))
    return ranked[:top]


def general_rules(traits):
    return [text for check, text in GENERAL_RULES if check(traits)]


COMBINATIONS_FILE = "combinations.json"


def load_combinations(data_dir=None):
    """Multi-game playbooks for complex situations (data/combinations.json)."""
    import json
    from pathlib import Path

    from .catalog import DATA_DIR

    path = Path(data_dir or DATA_DIR) / COMBINATIONS_FILE
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def matched_combinations(text, combinations):
    """Combinations whose phrases appear in the text, best matches first."""
    tokens = keywords._tokens(text)
    hits = []
    for combo in combinations:
        found = [p for p in combo["phrases"] if keywords.phrase_matches(tokens, p)]
        if found:
            hits.append({"combination": combo, "phrases": found})
    hits.sort(key=lambda hit: (-len(hit["phrases"]), hit["combination"]["name"]))
    return hits


def combined_rules(hits, count=3):
    """Strategies drawn from the top games, one per game, so the advice blends several models.

    Each entry is (game name, strategy). Games are taken in order; the first strategy from each.
    """
    rules = []
    for hit in hits[:count]:
        game = hit["game"]
        for strategy in game["strategies"][:2]:
            rules.append((game["name"], strategy))
    return rules
