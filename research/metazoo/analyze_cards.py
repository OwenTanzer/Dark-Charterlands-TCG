"""Summarize the features and characteristics of the scraped MetaZoo cards.

Reads cards.json (from scrape_cards.py) and writes FEATURES.md:
set sizes, aura and badge (rarity / card type) breakdowns, which stats each
card type carries, numeric stat distributions, trait / keyword / allied-aura
frequencies, ability counts, and the game terms used most in rules text.

Usage:
    python analyze_cards.py
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median

HERE = Path(__file__).resolve().parent


def table(headers: list[str], rows: list[list]) -> list[str]:
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return out + [""]


def counts(counter: Counter, total: int, top: int | None = None) -> list[list]:
    return [[k, n, f"{100 * n / total:.0f}%"] for k, n in counter.most_common(top)]


def num(v: str):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main():
    cards = json.loads((HERE / "cards.json").read_text(encoding="utf-8"))
    n = len(cards)
    md = ["# MetaZoo card features", "",
          f"{n} cards scraped from the official [MetaZoo card database](https://www.metazootcg.com/cards) "
          "by `scrape_cards.py`. Regenerate with `python analyze_cards.py`.", ""]

    sets = Counter((c["set_code"], c["set_name"]) for c in cards)
    md += ["## Sets", ""] + table(["Code", "Set", "Cards"], [[k[0], k[1], v] for k, v in sorted(sets.items())])

    auras = Counter(a for c in cards for a in c["auras"])
    multi = sum(len(c["auras"]) > 1 for c in cards)
    md += ["## Auras", "", f"{multi} cards have more than one Aura.", ""]
    md += table(["Aura", "Cards", "Share"], counts(auras, n))

    rarity = Counter(c["rarity"] or "(none: basic Aura / token)" for c in cards)
    md += ["## Rarity", ""] + table(["Rarity", "Cards", "Share"], counts(rarity, n))
    ctype = lambda c: " + ".join(c["card_types"]) or "(none)"
    types = Counter(ctype(c) for c in cards)
    md += ["## Card types", ""] + table(["Type", "Cards", "Share"], counts(types, n))

    by_type = defaultdict(list)
    for c in cards:
        by_type[ctype(c)].append(c)
    stat_keys = sorted({k for c in cards for k in c["stats"]})
    list_keys = sorted({k for c in cards for k in c["lists"]})
    md += ["## Which fields each card type has", "",
           "Share of cards of that type carrying the field.", ""]
    rows = []
    for t, group in sorted(by_type.items(), key=lambda kv: -len(kv[1])):
        row = [t, len(group)]
        for k in stat_keys:
            row.append(f"{100 * sum(k in c['stats'] for c in group) / len(group):.0f}%")
        for k in list_keys:
            row.append(f"{100 * sum(k in c['lists'] for c in group) / len(group):.0f}%")
        row.append(f"{mean(len(c['abilities']) for c in group):.1f}")
        rows.append(row)
    md += table(["Type", "Cards", *stat_keys, *list_keys, "Avg abilities"], rows)

    md += ["## Numeric stats", ""]
    rows = []
    for k in stat_keys:
        vals = [v for c in cards if (v := num(c["stats"].get(k))) is not None]
        if len(vals) >= 0.5 * sum(k in c["stats"] for c in cards) and vals:
            rows.append([k, len(vals), f"{min(vals):g}", f"{median(vals):g}", f"{mean(vals):.2f}", f"{max(vals):g}"])
    md += table(["Stat", "Cards", "Min", "Median", "Mean", "Max"], rows)
    for k in ("Cost", "Influence"):
        dist = Counter(c["stats"][k] for c in cards if k in c["stats"])
        if dist:
            ordered = sorted(dist.items(), key=lambda kv: (num(kv[0]) is None, num(kv[0]) or 0, kv[0]))
            md += [f"**{k} curve:** " + ", ".join(f"{v}: {cnt}" for v, cnt in ordered), ""]

    for k in stat_keys:
        vals = Counter(c["stats"][k] for c in cards if k in c["stats"])
        if num(next(iter(vals), None)) is None and 1 < len(vals) <= 12:
            md += [f"## {k}", ""] + table(["Value", "Cards", "Share"], counts(vals, sum(vals.values())))

    for k in list_keys:
        vals = Counter(v for c in cards for v in c["lists"].get(k, []))
        md += [f"## {k}", "", f"{sum(k in c['lists'] for c in cards)} cards, {len(vals)} distinct values.", ""]
        md += table(["Value", "Cards", "Share"], counts(vals, n, top=40))

    ab_count = Counter(len(c["abilities"]) for c in cards)
    vanilla = sum(not c["abilities"] for c in cards)
    md += ["## Abilities", "", "**Abilities per card:** " +
           ", ".join(f"{k}: {v}" for k, v in sorted(ab_count.items())), "",
           f"{vanilla} cards have no abilities. {sum(bool(c.get('flavor')) for c in cards)} cards carry flavor text, "
           f"and {sum(bool(c.get('subtitle')) for c in cards)} have a variant subtitle (e.g. \"At The Ready\").", ""]
    keywords = {v for c in cards for v in c["lists"].get("Keywords", [])}
    kinds, triggers, costs = Counter(), Counter(), Counter()
    for c in cards:
        for ab in c["abilities"]:
            t = ab["text"].strip()
            trig = re.match(r"((?:On|When|Whenever|At the start|At the end|At End|During|While|If|Once per)\b[^,:]*)", t)
            act = re.match(r"((?:\[[^\]]+\],?\s*)+):?|((?:Sacrifice|Discard|Tap)[^:.]{0,40}):", t)
            if act:
                kinds["Activated (pay a cost: effect)"] += 1
                costs[re.sub(r"\d+", "N", (act.group(1) or act.group(2)).strip(" ,:"))] += 1
            elif trig:
                kinds["Triggered (On / When / While / If ...)"] += 1
                triggers[" ".join(trig.group(1).split()[:5])] += 1
            elif t.split(" ")[0].rstrip(":") in keywords:
                kinds["Keyword-led (Discover, Overwhelm, Duel ...)"] += 1
            elif t.lower().startswith("choose one"):
                kinds["Modal (Choose one)"] += 1
            else:
                kinds["Static / one-shot effect"] += 1
    md += ["### Ability kinds", ""] + table(["Kind", "Abilities"], [[k, v] for k, v in kinds.most_common()])
    md += ["### Most common triggers (first 5 words)", ""] + table(["Trigger", "Abilities"], [[k, v] for k, v in triggers.most_common(20)])
    md += ["### Most common activation costs (numbers shown as N)", ""] + table(["Cost", "Abilities"], [[k, v] for k, v in costs.most_common(15)])
    terms = Counter(w for c in cards for ab in c["abilities"]
                    for w in re.findall(r"\b[A-Z][a-z]+(?: [A-Z][a-z]+)?\b", ab["text"])
                    if w not in {"On", "When", "Whenever", "If", "At", "While", "You", "Your", "This", "Then", "Each", "Once", "Give", "For"})
    md += ["### Capitalized game terms in rules text", "",
           "Capitalized words are usually defined game actions or keywords.", ""]
    md += table(["Term", "Mentions"], [[k, v] for k, v in terms.most_common(40)])

    md += ["## Data quirks", "",
           "- Some Trait values are misspelled in MetaZoo's own data (e.g. `Anomlay`, `Areial`) and are counted separately.",
           "- A few rules texts contain garbled characters (e.g. `ÃÂ¥` where a bullet should be). That is in the "
           "official site's data, not introduced by the scraper.", ""]

    artists = Counter(c["stats"].get("Artist", "(none)") for c in cards)
    md += ["## Artists", "", f"{len(artists)} distinct artists.", ""] + table(["Artist", "Cards"], [[k, v] for k, v in artists.most_common(15)])

    (HERE / "FEATURES.md").write_text("\n".join(md), encoding="utf-8")
    print(f"wrote FEATURES.md from {n} cards")


if __name__ == "__main__":
    main()
