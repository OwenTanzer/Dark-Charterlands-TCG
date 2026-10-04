# MetaZoo card research

Tools for inspecting the official [MetaZoo TCG card database](https://www.metazootcg.com/cards)
as a reference when designing original Dark Charterlands mechanics.

The sitemap spot-check on 2026-10-04 found 721 card-page URLs: Base Set (MZ1)
239, Torrential Tides (MZ2) 259, and Secret Shadows (MZ3) 223. These are page/printing
counts, including variants and tokens, not deduplicated card designs. The checked
sitemap did not include older pre-buyout sets. The committed `FEATURES.md` records
the author's original aggregate snapshot; its full private input was not available
for code review, so only the sitemap totals and one card's parsing were independently
spot-checked. No bulk scrape was run during review.

## Run

Requires Python 3.10 or newer. From this directory:

```sh
python -m pip install -r requirements.txt
python scrape_cards.py        # Full sitemap; roughly 12+ minutes on a cold cache
python analyze_cards.py       # Validates checksum/scope, then writes FEATURES.md
```

A partial run has separate outputs and cannot replace the full export or report:

```sh
python scrape_cards.py --limit 20   # Or --sets MZ1
python analyze_cards.py --partial  # Writes FEATURES.partial.md
```

Every run checks current `robots.txt` before reading the sitemap or card pages.
Only same-origin `/card/<SET>/<number>` URLs are followed; redirects and `/api`
are not used. Requests are at least one second apart (or a longer robots crawl
delay). Transient errors have bounded retries. Access denials and persistent rate
limits stop the run. Invalid/empty selections, bad pages and HTTP failures return
a nonzero exit status without replacing exports. Failed card URLs go to local
`failed.json`; a successful run removes that stale failure list.

## Output and provenance

| File | Purpose | In git? |
|---|---|---|
| `FEATURES.md` | Aggregate snapshot and interpretation caveats | Yes |
| `cards.json` / `cards.csv` | Full local card export, including rules text and image URLs | No |
| `cards.manifest.json` | Generation time, scope, counts, filters and JSON SHA-256 | No |
| `cards.partial.*` / `FEATURES.partial.md` | Filtered-run exports, manifest and report | No |
| `cache/` | Local raw card HTML | No |
| `failed.json` | Errors from a failed scrape | No |

The manifest is published last, after staging both exports. The analyzer refuses
missing/mismatched manifests, duplicate card identities, incomplete runs, and
incorrect scope/counts. A crash between replacements is detected by the JSON
checksum. Generation time is not a fresh-fetch timestamp: cached pages can be
older. To refresh an old cache, remove it locally before a permitted new run.
Legacy exports without a manifest must be regenerated before using the analyzer.

CSV stat/list columns use `stat:` / `list:` prefixes to avoid field-name collisions.
Potential spreadsheet formulas are prefixed with an apostrophe; JSON preserves
original field text. Header identity and page structure are checked before new
HTML is cached. UTF-8 is decoded explicitly rather than using an implicit Latin-1
fallback. New labelled stats and list fields are retained without code changes.

Ability kinds and capitalized terms are text heuristics, not official rules
classifications. In particular, `While`/`If` can describe static conditions, and
bracketed text can be an annotation rather than an activation cost.

## Rights and use boundary

This is an unofficial research tool. The full export, raw pages and artwork stay
out of git. The scraper records image URLs; it does not download artwork.
Robots permission is not a license to redistribute card text or art. Review the
current [Terms of Service](https://www.metazootcg.com/terms-of-service) and
[Fan Content Policy](https://www.metazootcg.com/fan-content-policy) before reuse.
The fan policy permits various community resources but restricts asset collections,
commercial reuse and substitute/competing products. Do not treat this repository
as permission to copy MetaZoo assets into Dark Charterlands or publish a full dump.
Questions about planned reuse need separate rights review or permission.

## Offline tests

From the repository root:

```sh
python -m unittest discover -s research/metazoo -p 'test_*.py' -v
python -m py_compile research/metazoo/*.py
```

Tests use invented HTML and mocked HTTP responses. They make no live network
requests and contain no MetaZoo card rules text or artwork.
