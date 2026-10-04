"""Minimum complete-card contract shared by the scraper and analyzer.

All current card categories, including basic Auras and tokens, carry Cost and
Influence. Rarity, Artist, lists and abilities may legitimately be absent/empty.
Unknown additional fields are preserved; these checks do not prescribe their values.
"""
import re

BASE = "https://www.metazootcg.com"
CARD_URL = re.compile(re.escape(BASE) + r"/card/([A-Za-z0-9_-]+)/(\d+)$")
CARD_TYPES = {"Creature", "Strategy", "Equipment", "Terra", "Caster", "Aura"}


def nonempty_text(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_card(card: dict) -> None:
    """Reject incomplete/malformed records before caching, exporting or analysis."""
    required = {"set_code", "set_name", "number", "url", "name", "auras", "rarity", "card_types", "stats", "lists", "abilities"}
    if not isinstance(card, dict) or not required <= card.keys():
        raise ValueError("card is missing required fields")
    if not all(nonempty_text(card[k]) for k in ("set_code", "set_name", "url", "name")):
        raise ValueError("card identity/name fields must be nonempty text")
    match = CARD_URL.fullmatch(card["url"])
    if (type(card["number"]) is not int or not match
            or match[1] != card["set_code"] or int(match[2]) != card["number"]):
        raise ValueError("card identity does not match its source URL")
    if (not isinstance(card["auras"], list) or not card["auras"]
            or not all(nonempty_text(a) for a in card["auras"])):
        raise ValueError("card must carry at least one Aura")
    if (not isinstance(card["card_types"], list) or not card["card_types"]
            or not all(isinstance(t, str) and t in CARD_TYPES for t in card["card_types"])):
        raise ValueError("card must carry recognized card types")
    if not isinstance(card["rarity"], str):
        raise ValueError("rarity must be text (empty is allowed)")
    stats = card["stats"]
    if (not isinstance(stats, dict)
            or not all(nonempty_text(k) and isinstance(v, str) for k, v in stats.items())
            or not all(nonempty_text(stats.get(k)) for k in ("Cost", "Influence"))):
        raise ValueError("card must carry nonempty Cost and Influence stats")
    lists = card["lists"]
    if (not isinstance(lists, dict)
            or not all(nonempty_text(k) and isinstance(v, list)
                       and all(nonempty_text(item) for item in v) for k, v in lists.items())):
        raise ValueError("card list fields must contain text lists")
    abilities = card["abilities"]
    if (not isinstance(abilities, list)
            or not all(isinstance(a, dict) and isinstance(a.get("name"), str)
                       and nonempty_text(a.get("text")) for a in abilities)):
        raise ValueError("ability sections must contain rules text (an empty abilities list is allowed)")
