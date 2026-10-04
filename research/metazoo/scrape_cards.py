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
import hashlib
import math
import os
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.robotparser import RobotFileParser
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from card_schema import BASE, CARD_URL, CARD_TYPES, validate_card

HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
HEADERS = {"User-Agent": "Dark-Charterlands-TCG research scraper (personal, non-commercial)"}


def request_text(session: requests.Session, url: str, delay: float) -> str:
    """Read UTF-8 public text, with bounded retries and no redirect following."""
    for attempt in range(3):
        try:
            resp = session.get(url, timeout=30, allow_redirects=False)
        finally:
            time.sleep(delay)  # Transport failures must still respect pacing.
        if resp.is_redirect:
            raise ValueError(f"refusing redirect from {url}")
        if resp.status_code == 429 or resp.status_code >= 500:
            if attempt < 2:
                try:
                    retry_after = float(resp.headers.get("Retry-After", "0"))
                except ValueError:
                    retry_after = 0
                # Long or dated Retry-After responses need a later manual retry.
                if (not math.isfinite(retry_after) or retry_after > 60
                        or (resp.headers.get("Retry-After") and retry_after == 0)):
                    resp.raise_for_status()
                time.sleep(max(5 * (attempt + 1), retry_after))
                continue
        resp.raise_for_status()
        # The source is UTF-8. Do not use requests' implicit Latin-1 fallback,
        # which can permanently introduce mojibake into the local cache.
        return resp.content.decode("utf-8-sig")
    raise RuntimeError("request attempts exhausted")


def robots_policy(session: requests.Session, delay: float) -> tuple[RobotFileParser, float]:
    policy = RobotFileParser(f"{BASE}/robots.txt")
    policy.parse(request_text(session, policy.url, delay).splitlines())
    crawl_delay = policy.crawl_delay(HEADERS["User-Agent"])
    return policy, max(delay, crawl_delay or 0)


def card_urls(session: requests.Session, delay: float = 1.0) -> list[str]:
    xml = request_text(session, f"{BASE}/sitemap.xml", delay)
    root = ET.fromstring(xml)
    urls = {el.text.strip() for el in root.iter()
            if el.tag.rsplit("}", 1)[-1] == "loc" and el.text
            and CARD_URL.fullmatch(el.text.strip())}
    if not urls:
        raise ValueError("sitemap contained no supported card URLs")
    return sorted(urls, key=lambda u: (CARD_URL.fullmatch(u)[1], int(CARD_URL.fullmatch(u)[2])))


def fetch(session: requests.Session, url: str, delay: float) -> str:
    match = CARD_URL.fullmatch(url)
    if not match:
        raise ValueError("unsupported card URL")
    set_code, num = match.groups()
    path = CACHE / set_code / f"{int(num):04d}.html"
    if path.exists():
        return path.read_text(encoding="utf-8")
    html = request_text(session, url, delay)
    parse_card(html, url)  # Never cache a successful HTTP error/interstitial page.
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return html


def text(el) -> str:
    return " ".join(el.get_text(" ", strip=True).split()) if el else ""


class ArticleCompletionParser(HTMLParser):
    """Observe source tokens, without repairing unclosed card markup.

    HTMLParser treats comments, quoted attributes and script/style bodies as
    content, so a literal "</article>" inside them is not a closing-tag token.
    Only the first article is checked, matching BeautifulSoup.find below.
    """
    def __init__(self):
        super().__init__()
        self.article_depth = 0
        self.complete = False
        self.text_container = None

    def handle_starttag(self, tag, attrs):
        if self.text_container:
            return
        if tag in {"script", "style", "textarea", "title"}:
            self.text_container = tag
        if tag == "article" and not self.complete:
            self.article_depth += 1

    def handle_endtag(self, tag):
        if self.text_container:
            if tag == self.text_container:
                self.text_container = None
            return
        if tag == "article" and self.article_depth:
            self.article_depth -= 1
            if self.article_depth == 0:
                self.complete = True


def require_complete_article(html: str) -> None:
    parser = ArticleCompletionParser()
    parser.feed(html)
    parser.close()
    if not parser.complete:
        raise ValueError("card source has no complete article; response may be truncated")


def parse_card(html: str, url: str) -> dict:
    require_complete_article(html)
    soup = BeautifulSoup(html, "html.parser")
    art = soup.find("article")
    if art is None or art.find("h1") is None or art.find("header") is None:
        raise ValueError("no card <article> on page")
    header = art.find("header")
    match = CARD_URL.fullmatch(url)
    if not match:
        raise ValueError("unsupported card URL")
    set_code, num = match.groups()
    card = {"set_code": set_code, "number": int(num), "url": url}

    set_line = text(header.find("p"))  # "Base Set · MZ1 # 1"
    if not re.search(rf"\b{re.escape(set_code)}\s*#\s*0*{int(num)}\b", set_line):
        raise ValueError("card header identity does not match URL")
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
            value = dt.find_next_sibling()
            stats[text(dt)] = text(value) if value and value.name == "dd" else ""
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
    validate_card(card)
    return card


def write_csv(cards: list[dict], path: Path) -> None:
    stat_keys = sorted({k for c in cards for k in c["stats"]})
    list_keys = sorted({k for c in cards for k in c["lists"]})
    max_ab = max((len(c["abilities"]) for c in cards), default=0)
    cols = ["set_code", "set_name", "number", "name", "subtitle", "auras", "rarity", "card_types",
            *[f"stat:{k}" for k in stat_keys], *[f"list:{k}" for k in list_keys]]
    for i in range(1, max_ab + 1):
        cols += [f"ability_{i}_name", f"ability_{i}_text"]
    cols += ["flavor", "url", "image"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([csv_safe(v) for v in cols])
        for c in cards:
            row = {k: c[k] for k in ("set_code", "set_name", "number", "name", "subtitle", "rarity",
                                     "flavor", "url", "image")}
            row["auras"] = "; ".join(c["auras"])
            row["card_types"] = "; ".join(c["card_types"])
            row.update({f"stat:{k}": v for k, v in c["stats"].items()})
            row.update({f"list:{k}": "; ".join(v) for k, v in c["lists"].items()})
            for i, ab in enumerate(c["abilities"], 1):
                row[f"ability_{i}_name"], row[f"ability_{i}_text"] = ab["name"], ab["text"]
            w.writerow([csv_safe(row.get(k, "")) for k in cols])


def csv_safe(value):
    """Keep untrusted page text from becoming spreadsheet formulas."""
    if isinstance(value, str) and (value.startswith(("\t", "\r", "\n"))
                                  or value.lstrip().startswith(("=", "+", "-", "@"))):
        return "'" + value
    return value


def write_exports(cards: list[dict], stem: str, manifest: dict) -> None:
    """Stage both exports, then publish the checksum manifest last.

    A process interruption between replacements is detected by the analyzer's
    checksum check. Scrape failures never enter this function.
    """
    for card in cards:
        validate_card(card)
    with tempfile.TemporaryDirectory(dir=HERE) as staging:
        staging = Path(staging)
        json_path = staging / f"{stem}.json"
        json_path.write_text(json.dumps(cards, indent=2, ensure_ascii=False), encoding="utf-8")
        write_csv(cards, staging / f"{stem}.csv")
        manifest["cards_sha256"] = hashlib.sha256(json_path.read_bytes()).hexdigest()
        (staging / f"{stem}.manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        for suffix in ("json", "csv", "manifest.json"):
            os.replace(staging / f"{stem}.{suffix}", HERE / f"{stem}.{suffix}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--delay", type=float, default=1.0, help="Seconds between requests (minimum/default 1)")
    ap.add_argument("--limit", type=int, default=None, help="Only the first N cards; writes cards.partial.*")
    ap.add_argument("--sets", type=str, default=None, help="Comma-separated set codes; writes cards.partial.*")
    args = ap.parse_args(argv)
    if not math.isfinite(args.delay) or args.delay < 1:
        ap.error("--delay must be finite and at least 1 second")
    if args.limit is not None and args.limit <= 0:
        ap.error("--limit must be positive")

    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        policy, delay = robots_policy(session, args.delay)
        if not policy.can_fetch(HEADERS["User-Agent"], f"{BASE}/sitemap.xml"):
            raise ValueError("robots.txt disallows sitemap access")
        all_urls = card_urls(session, delay)
        urls = all_urls
        if args.sets is not None:
            wanted = {s.strip().upper() for s in args.sets.split(",")}
            available = {CARD_URL.fullmatch(u)[1].upper() for u in urls}
            if not wanted or not wanted <= available:
                raise ValueError("--sets must name nonempty set codes present in the sitemap")
            urls = [u for u in urls if CARD_URL.fullmatch(u)[1].upper() in wanted]
        if args.limit is not None:
            urls = urls[:args.limit]
        if any(not policy.can_fetch(HEADERS["User-Agent"], u) for u in urls):
            raise ValueError("robots.txt disallows one or more selected card pages")
        print(f"{len(urls)} card pages", file=sys.stderr)

        cards, failed = [], []
        for i, url in enumerate(urls, 1):
            try:
                cards.append(parse_card(fetch(session, url, delay), url))
            except (requests.RequestException, ValueError, UnicodeError) as e:
                failed.append({"url": url, "error": str(e)})
                response = getattr(e, "response", None)
                if isinstance(e, requests.RequestException) and (response is None
                        or response.status_code in (401, 403, 429) or response.status_code >= 500):
                    break  # Stop on connection failure, denial, or persistent overload.
            if i % 50 == 0 or i == len(urls):
                print(f"  {i}/{len(urls)} ({len(failed)} failed)", file=sys.stderr)
        if failed:
            (HERE / "failed.json").write_text(json.dumps(failed, indent=2), encoding="utf-8")
            print(f"{len(failed)} pages failed; existing exports were not changed. See failed.json.", file=sys.stderr)
            return 1
        partial = args.sets is not None or args.limit is not None
        stem = "cards.partial" if partial else "cards"
        write_exports(cards, stem, {
            "schema_version": 2,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "source_sitemap": f"{BASE}/sitemap.xml",
            "scope": "filtered" if partial else "full_sitemap",
            "filters": {"sets": args.sets, "limit": args.limit},
            "sitemap_count": len(all_urls),
            "selected_count": len(urls),
            "parsed_count": len(cards),
            "failed_count": 0,
            "set_counts": dict(sorted(Counter(c["set_code"] for c in cards).items())),
            "cache_note": "Pages can come from earlier cached fetches; generation time is not a fresh-source timestamp.",
        })
        (HERE / "failed.json").unlink(missing_ok=True)
        print(f"wrote {len(cards)} cards to {stem}.json / {stem}.csv and checksum manifest", file=sys.stderr)
        return 0
    except (requests.RequestException, ValueError, UnicodeError, ET.ParseError, OSError) as e:
        print(f"Scrape failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
