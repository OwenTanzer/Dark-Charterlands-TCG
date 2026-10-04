"""Scrape every card from the official MetaZoo TCG card database
(https://www.metazootcg.com/cards) into cards.json / cards.csv.

How it works:
1. Card page URLs come from the site's sitemap.xml (/card/<SET>/<number>).
2. Each card page is fetched once and cached under cache/ so reruns are
   free. Requests are spaced by --delay seconds; /api is disallowed by the
   site's robots.txt, so this reads only the public HTML pages.
3. Each page's <article> is parsed generically, so a field the site adds
   later still shows up without code changes:
   - header line   -> set name, set code, card number
   - <h1>          -> card name (+ variant subtitle, e.g. "At The Ready")
   - header chips  -> auras (coloured chips) and badges (rarity, card type...)
   - <dl> pairs    -> any labelled stat (Cost, Influence, Artist, ...)
   - label + chips -> list fields (Allied Auras, ...)
   - <section>s    -> abilities (name + rules text)
   - <blockquote>  -> flavor text

Usage:
    python scrape_cards.py                  # all cards
    python scrape_cards.py --limit 20       # quick test
    python scrape_cards.py --sets MZ1,MZ2   # only some sets
"""
import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE = "https://www.metazootcg.com"
HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
HEADERS = {"User-Agent": "Dark-Charterlands-TCG research scraper (personal, non-commercial)"}
CARD_URL = re.compile(r"/card/([^/]+)/(\d+)$")
CARD_TYPES = {"Creature", "Strategy", "Equipment", "Terra", "Caster", "Aura"}


def card_urls(session: requests.Session) -> list[str]:
    xml = session.get(f"{BASE}/sitemap.xml", timeout=30).text
    urls = [u for u in re.findall(r"<loc>([^<]+)</loc>", xml) if CARD_URL.search(u)]
    return sorted(set(urls), key=lambda u: (CARD_URL.search(u)[1], int(CARD_URL.search(u)[2])))


def fetch(session: requests.Session, url: str, delay: float) -> str:
    set_code, num = CARD_URL.search(url).groups()
    path = CACHE / set_code / f"{int(num):04d}.html"
    if path.exists():
        return path.read_text(encoding="utf-8")
    for attempt in range(3):
        resp = session.get(url, timeout=30)
        if resp.status_code == 429 or resp.status_code >= 500:
            time.sleep(5 * (attempt + 1))
            continue
        resp.raise_for_status()
        break
    else:
        resp.raise_for_status()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(resp.text, encoding="utf-8")
    time.sleep(delay)
    return resp.text


def text(el) -> str:
    return " ".join(el.get_text(" ", strip=True).split()) if el else ""


def parse_card(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    art = soup.find("article")
    if art is None or art.find("h1") is None:
        raise ValueError("no card <article> on page")
    header = art.find("header")
    set_code, num = CARD_URL.search(url).groups()
    card = {"set_code": set_code, "number": int(num), "url": url}

    set_line = text(header.find("p"))  # "Base Set · MZ1 # 1"
    card["set_name"] = set_line.split("·")[0].strip()
    h1 = art.find("h1")
    sub = h1.find("span")  # "— At The Ready" variant subtitle
    card["subtitle"] = text(sub).lstrip("—").strip() if sub else ""
    if sub:
        sub.extract()
    card["name"] = text(h1)

    auras, badges = [], []
    for chip in header.select("div > span"):
        (auras if "background-color" in (chip.get("style") or "") else badges).append(text(chip))
    card["auras"] = auras
    card["badges"] = badges
    # badge order isn't fixed: basic Aura cards and tokens have no rarity, and
    # some cards are both Creature and Equipment
    card["card_types"] = [b for b in badges if b in CARD_TYPES]
    card["rarity"] = next((b for b in badges if b not in CARD_TYPES), "")

    stats = {}
    dl = art.find("dl")
    if dl:
        for dt in dl.find_all("dt"):
            stats[text(dt)] = text(dt.find_next_sibling("dd"))
    card["stats"] = stats

    lists = {}
    for group in art.find_all("div", recursive=False):
        spans = group.find_all("span", recursive=False)
        if len(spans) >= 2:
            lists[text(spans[0])] = [text(s) for s in spans[1:]]
    card["lists"] = lists

    card["abilities"] = [
        {"name": text(sec.find("h3")), "text": sec.find("p").get_text("\n", strip=True) if sec.find("p") else ""}
        for sec in art.find_all("section")
    ]
    card["flavor"] = text(art.find("blockquote"))

    img = soup.find("meta", property="og:image")
    pic = soup.find("img", alt=card["name"])
    card["image"] = img["content"] if img else (pic.get("src") if pic else "")
    return card


def write_csv(cards: list[dict], path: Path) -> None:
    stat_keys = sorted({k for c in cards for k in c["stats"]})
    list_keys = sorted({k for c in cards for k in c["lists"]})
    max_ab = max((len(c["abilities"]) for c in cards), default=0)
    cols = ["set_code", "set_name", "number", "name", "subtitle", "auras", "rarity", "card_types",
            *stat_keys, *list_keys]
    for i in range(1, max_ab + 1):
        cols += [f"ability_{i}_name", f"ability_{i}_text"]
    cols += ["flavor", "url", "image"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for c in cards:
            row = {k: c[k] for k in ("set_code", "set_name", "number", "name", "subtitle", "rarity",
                                     "flavor", "url", "image")}
            row["auras"] = "; ".join(c["auras"])
            row["card_types"] = "; ".join(c["card_types"])
            row.update(c["stats"])
            row.update({k: "; ".join(v) for k, v in c["lists"].items()})
            for i, ab in enumerate(c["abilities"], 1):
                row[f"ability_{i}_name"], row[f"ability_{i}_text"] = ab["name"], ab["text"]
            w.writerow(row)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--delay", type=float, default=1.0, help="Seconds between uncached requests (default 1)")
    ap.add_argument("--limit", type=int, default=None, help="Only the first N cards")
    ap.add_argument("--sets", type=str, default=None, help="Comma-separated set codes, e.g. MZ1,MZ2")
    args = ap.parse_args()

    session = requests.Session()
    session.headers.update(HEADERS)
    urls = card_urls(session)
    if args.sets:
        wanted = {s.strip().upper() for s in args.sets.split(",")}
        urls = [u for u in urls if CARD_URL.search(u)[1].upper() in wanted]
    if args.limit:
        urls = urls[:args.limit]
    print(f"{len(urls)} card pages", file=sys.stderr)

    cards, failed = [], []
    for i, url in enumerate(urls, 1):
        try:
            cards.append(parse_card(fetch(session, url, args.delay), url))
        except (requests.RequestException, ValueError) as e:
            failed.append({"url": url, "error": str(e)})
        if i % 50 == 0 or i == len(urls):
            print(f"  {i}/{len(urls)} ({len(failed)} failed)", file=sys.stderr)

    (HERE / "cards.json").write_text(json.dumps(cards, indent=2, ensure_ascii=False), encoding="utf-8")
    write_csv(cards, HERE / "cards.csv")
    if failed:
        (HERE / "failed.json").write_text(json.dumps(failed, indent=2), encoding="utf-8")
    print(f"wrote {len(cards)} cards to cards.json / cards.csv; {len(failed)} failed", file=sys.stderr)


if __name__ == "__main__":
    main()
