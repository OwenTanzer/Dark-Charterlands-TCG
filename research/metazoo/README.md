# MetaZoo card research

Pulls every card from the official [MetaZoo TCG card database](https://www.metazootcg.com/cards)
so we can see which features and characteristics MetaZoo cards use, as reference
for designing Dark Charterlands.

The official site covers the current MetaZoo sets: Base Set (MZ1), Torrential
Tides (MZ2) and Secret Shadows (MZ3), 721 cards in all. Older sets from before the
buyout (Cryptid Nation, Seance, UFO, etc.) aren't on it.

## Run

```
pip install -r requirements.txt
python scrape_cards.py        # ~12 min the first time (1 request/s), instant after that from cache/
python analyze_cards.py       # writes FEATURES.md
```

`scrape_cards.py --limit 20` or `--sets MZ1` gives a quick partial run.

## Output

| File | What it is | In git? |
|---|---|---|
| `FEATURES.md` | Summary: sets, Auras, rarities, card types, which fields each type has, Cost/Influence curves, traits, keywords, ability triggers, common rules terms | Yes |
| `cards.json` | Every card: set, number, name, Auras, badges (rarity, type), stats (Cost, Influence, Artist, Aura Enhanceable...), lists (Traits, Keywords, Allied Auras), abilities, image URL | No (local) |
| `cards.csv` | The same data flattened for a spreadsheet | No (local) |
| `cache/` | Raw card pages, so reruns don't hit the site | No |

The card dump stays out of git because this repo is public and the card text
and art belong to MetaZoo. Run the scraper locally to get it.

## How it scrapes

- Card URLs come from the site's `sitemap.xml`.
- It reads only public card pages. The site's robots.txt disallows `/api`, so
  the scraper doesn't use it.
- Each card page's `<article>` is parsed generically (labelled stats, chip
  lists, ability sections), so any new field the site adds shows up in the
  output without code changes.
