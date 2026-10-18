"""Write gtplaybook/data/keywords.json from the game phrases and the family words.

Run from the project root:  python3 tools/keywords/build_keywords.py
It fails if any game has no phrases, so every game can be found by a description.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT))

from game_phrases import GAME_PHRASES  # noqa: E402
from gtplaybook.catalog import load_games, load_areas  # noqa: E402

FAMILY_WORDS = {
    "Classic game theory": ["classic", "dilemma", "game theory", "textbook"],
    "Traditional and parlour games": ["cards", "dice", "board game", "parlour", "bluff"],
    "Life games": ["everyday", "life", "home", "family", "daily"],
    "War and security games": ["war", "military", "security", "deterrence", "army", "conflict"],
    "Work games": ["work", "job", "office", "boss", "employee", "career", "workplace", "team"],
    "Government and politics": ["government", "politics", "election", "parliament", "regime", "policy", "power"],
    "Society and groups": ["society", "group", "community", "social", "movement", "people"],
    "Business and markets": ["business", "market", "company", "firm", "price", "customer", "competition"],
    "Economics and finance": ["economy", "finance", "bank", "money", "investment", "economic"],
    "Negotiation and fairness": ["negotiate", "negotiation", "fair", "deal", "bargain", "settle"],
    "Public goods and environment": ["environment", "public", "shared", "climate", "resource", "commons"],
    "Games against AI": ["ai", "bot", "computer", "machine", "algorithm"],
    "AI vs AI (multi-agent)": ["ai", "agents", "algorithms", "learning", "self play"],
    "Evolution and biology": ["evolution", "biology", "population", "nature", "animals"],
    "Intelligence and deception": ["intelligence", "spy", "deception", "secret", "warning", "analysis"],
    "Pandemic and disaster": ["pandemic", "disaster", "outbreak", "emergency", "health", "crisis"],
    "Advanced game theory": ["mechanism", "auction", "information design", "coalition", "credible", "equilibrium"],
}


def main():
    games = load_games()
    missing = [g["id"] for g in games if not GAME_PHRASES.get(g["id"])]
    unknown = [gid for gid in GAME_PHRASES if gid not in {g["id"] for g in games}]
    if missing or unknown:
        print("missing phrases:", missing, "unknown ids:", unknown, file=sys.stderr)
        return 1
    families = [area["family"] for area in load_areas()]
    missing_families = [f for f in families if f not in FAMILY_WORDS]
    if missing_families:
        print("families without words:", missing_families, file=sys.stderr)
        return 1
    data = {
        "games": {g["id"]: GAME_PHRASES[g["id"]] for g in games},
        "families": {f: FAMILY_WORDS[f] for f in families},
    }
    out = ROOT / "gtplaybook" / "data" / "keywords.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    phrases = sum(len(v) for v in data["games"].values())
    print(f"wrote {len(data['games'])} games ({phrases} phrases) and {len(data['families'])} families to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
