"""Parses scenario files and plain-English descriptions into game traits."""

import re

from .catalog import TRAITS


class ScenarioError(ValueError):
    pass


# Keyword rules that turn a sentence into traits. For the same key, later rules
# override earlier ones, so the more specific patterns go last.
RULES = [
    ("players", "two", r"\b(two|2|duopol\w*|head[- ]to[- ]head|one[- ]on[- ]one|bilateral|between two)\b"),
    ("players", "many", r"\b(many|several|dozens?|hundreds?|everyone|(?:[3-9]|\d{2,}) (?:players|firms|people|countries|nations|boats|compan\w*|bidders|members|teams|parties))\b"),
    ("timing", "simultaneous", r"simultaneous\w*|at the same time|sealed|blind|without (?:knowing|seeing)|independent(?:ly)? decid\w*|both (?:choose|decide|pick|move)"),
    ("timing", "sequential", r"goes first|go first|first mover|moves? first|turns? to|in response|after (?:they|he|she|it|the other)|sequential\w*|leader|follower|escalat\w*|then (?:they|he|she|the other)"),
    ("interaction", "repeated", r"repeat\w*|again and again|ongoing|every (?:day|week|month|year|season|round)|long[- ]term|recurring|future (?:dealings|rounds|business)|keep (?:dealing|working)|will (?:meet|deal|work) again"),
    ("interaction", "one-shot", r"one[- ]time|one[- ]shot|single (?:round|encounter|time|deal)|never (?:\w+ ){0,3}again|\bonce\b"),
    ("information", "imperfect", r"hidden|private information|don'?t know|unknown|imperfect|asymmetric|can'?t (?:see|observe|verify|tell)|secret|bluff\w*|unobservable|not sure|uncertain\w*"),
    ("information", "perfect", r"(?<!im)perfect information|fully observ\w*|everyone (?:can )?(?:see|knows)|open information"),
    ("payoff", "mixed", r"cooperat\w*|collaborat\w*|partner\w*|trad(?:e|ing)|both (?:sides|parties|of us) (?:benefit|gain|win)|mutual(?:ly)? (?:benefit|gain)|compet\w*"),
    ("payoff", "common-interest", r"common (?:interest|goal)|same goal|team ?work|same team|both win together|shared goal"),
    ("payoff", "zero-sum", r"zero[- ]sum|win[- ]lose|winner takes all|fixed (?:pie|prize)|must lose|battlefield\w*|enemy|opponent wins|one side'?s gain"),
    ("communication", "yes", r"\btalk\w*|\bchat\w*|messag\w*|communicat\w*|discuss\w*|signal\w*|promis\w*|negotiat\w*|speak"),
    ("communication", "no", r"no (?:communication|talking|contact)|can'?t (?:talk|communicate|speak)|silent|no way to talk"),
    ("enforcement", "yes", r"contract\w*|enforc\w*|legal\w*|penalt\w*|court\w*|binding|punish\w*|sanction\w*|regulat\w*|inspect\w*|audit\w*|fines?\b|police"),
    ("enforcement", "no", r"no (?:contract|enforcement|penalt|rules)|unenforceable|nothing stops|no way to (?:enforce|hold)"),
    ("commitment", "yes", r"commit\w*|threat\w*|can'?t back down|irreversib\w*|credib\w*|pre-?commit\w*|lock (?:in|ourselves|themselves)|cannot (?:retreat|back out)|no turning back|burn (?:the|our) bridges"),
    ("commitment", "no", r"no commitment|can (?:always )?change (?:my|our|their) mind|(?<!ir)reversible|can backtrack"),
    ("bargaining", "yes", r"negotiat\w*|bargain\w*|salary|pric\w*|split\w*|divid\w*|haggl\w*|offer\w*|settle\w*|deal\b|share the"),
]

DOMAIN_WORDS = {
    "work": r"\bwork\b|salary|\bjob|boss|employer|coworker|co-worker|colleague|promotion|hiring|office\b|manager|\braise\b|team\b|power\b|hierarch\w*|dominan\w*",
    "business": r"\bbusiness\b|compan\w*|\bfirms?\b|market|customer|pric\w*|startup|investor|supplier|competitor|client|auction|monopol\w*|profit\w*",
    "military": r"\bmilitary\b|army|military|troop|\bwar\b|battle|defen[cs]e|attack|weapon|deter\w*|nuclear|front\b|enem\w*|invasion|soldier",
    "politics": r"\bpolitics\b|election|vote\w*|government|parliament|policy|coalition|senate|campaign|treat(?:y|ies)|diplomat\w*|countr\w*|nation\w*|politic\w*|power\b|dominan\w*",
    "games": r"\bgames\b|\bgames?\b|poker|chess|sport\w*|tournament|\bplayers?\b|\bmatch\b",
    "everyday": r"\beveryday\b|roommate|family|friend\w*|partner|dinner|chore|neighbou?r|kids?\b|sibling|relationship|household",
    "economy": r"\beconomy\b|econom\w*|\btax\w*|public good|commons|resource\w*|subsid\w*",
    "environment": r"\benvironment\b|environment\w*|climate|fish\w*|pollut\w*|forest|water|emission\w*|wildlife",
    "government": r"\bgovernment\b|government\w*|regime|dictat\w*|autocra\w*|junta|coup\w*|cabinet|minister\w*|coalition|succession|opposition|protest\w*|revolution\w*|uprising|resistance",
    "society": r"\bsociety\b|cult\w*|religio\w*|community|social\w*|coercive|whistle\w*|movement",
}

TEMPLATE = """\
# Scenario file. One 'key: value' per line. Lines starting with '#' are comments.
#
# Trait keys and their values:
#   players:        two | many   (a number also works, e.g. 2 or 5)
#   timing:         simultaneous | sequential
#   interaction:    one-shot | repeated
#   information:    perfect | imperfect
#   payoff:         zero-sum | mixed | common-interest
#   communication, enforcement, commitment, bargaining:  yes | no
#
# Optional keys:
#   title:   a name for the situation
#   domain:  comma-separated, from work, business, military, politics,
#            games, everyday, economy, environment
#   notes:   free text, ignored by the advisor

title: My situation
players: two
timing: sequential
interaction: one-shot
information: imperfect
payoff: mixed
communication: yes
enforcement: no
commitment: no
bargaining: yes
domain: work
notes: Free text, ignored by the advisor
"""


def normalise(key, value):
    """Return a validated trait value, accepting a few common aliases."""
    if key not in TRAITS:
        raise ScenarioError(f"unknown trait '{key}'")
    value = value.strip().lower()
    if key == "players" and value.isdigit():
        value = "two" if int(value) == 2 else "many"
    value = {"true": "yes", "false": "no", "y": "yes", "n": "no"}.get(value, value)
    if value not in TRAITS[key]:
        raise ScenarioError(f"'{key}' must be {' | '.join(TRAITS[key])}, got '{value}'")
    return value


def parse_domains(value):
    domains = [part.strip().lower() for part in value.split(",") if part.strip()]
    unknown = [domain for domain in domains if domain not in DOMAIN_WORDS]
    if unknown:
        raise ScenarioError(f"unknown domain(s) {', '.join(unknown)}; choose from {', '.join(DOMAIN_WORDS)}")
    return domains


def parse_scenario(text):
    """Parse the 'key: value' scenario format into a dict with traits and domains."""
    scenario = {"title": "", "notes": "", "domains": [], "traits": {}}
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ScenarioError(f"line {lineno}: expected 'key: value', got '{line}'")
        key, value = (part.strip() for part in line.split(":", 1))
        key = key.lower()
        try:
            if key == "title":
                scenario["title"] = value
            elif key == "notes":
                scenario["notes"] = value
            elif key == "domain":
                scenario["domains"] = parse_domains(value)
            else:
                scenario["traits"][key] = normalise(key, value)
        except ScenarioError as exc:
            raise ScenarioError(f"line {lineno}: {exc}") from None
    return scenario


def describe(text):
    """Infer traits from a plain-English description. The evidence is returned so the user can check it."""
    lowered = text.lower()
    traits, evidence = {}, {}
    for key, value, pattern in RULES:
        match = re.search(pattern, lowered)
        if match:
            traits[key] = value
            evidence[key] = match.group(0)
    domains = [name for name, pattern in DOMAIN_WORDS.items() if re.search(pattern, lowered)]
    return {
        "title": text.strip()[:70],
        "text": text.strip(),
        "notes": "",
        "domains": domains,
        "traits": traits,
        "evidence": evidence,
    }
