# MetaZoo card features

721 cards scraped from the official [MetaZoo card database](https://www.metazootcg.com/cards) by `scrape_cards.py`. Regenerate with `python analyze_cards.py`.

## Sets

| Code | Set | Cards |
|---|---|---|
| MZ1 | Base Set | 239 |
| MZ2 | Torrential Tides | 259 |
| MZ3 | Secret Shadows | 223 |

## Auras

0 cards have more than one Aura.

| Aura | Cards | Share |
|---|---|---|
| Air | 132 | 18% |
| Earth | 131 | 18% |
| Fire | 130 | 18% |
| Lightning | 130 | 18% |
| Water | 115 | 16% |
| Dark | 83 | 12% |

## Rarity

| Rarity | Cards | Share |
|---|---|---|
| Common | 197 | 27% |
| Uncommon | 156 | 22% |
| Rare | 139 | 19% |
| Super Rare | 99 | 14% |
| Alt Art | 76 | 11% |
| Legend | 27 | 4% |
| Hidden | 19 | 3% |
| (none: basic Aura / token) | 8 | 1% |

## Card types

| Type | Cards | Share |
|---|---|---|
| Creature | 412 | 57% |
| Strategy | 117 | 16% |
| Equipment | 81 | 11% |
| Terra | 59 | 8% |
| Caster | 41 | 6% |
| Aura | 6 | 1% |
| Creature + Equipment | 5 | 1% |

## Which fields each card type has

Share of cards of that type carrying the field.

| Type | Cards | Artist | Aura Enhanceable | Cost | Influence | Location | Allied Auras | Keywords | Subtype | Traits | Avg abilities |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Creature | 412 | 99% | 100% | 100% | 100% | 67% | 0% | 27% | 26% | 100% | 0.9 |
| Strategy | 117 | 100% | 100% | 100% | 100% | 0% | 0% | 15% | 0% | 0% | 1.0 |
| Equipment | 81 | 99% | 100% | 100% | 100% | 2% | 0% | 10% | 25% | 9% | 0.9 |
| Terra | 59 | 100% | 100% | 100% | 100% | 0% | 0% | 8% | 41% | 100% | 1.0 |
| Caster | 41 | 100% | 100% | 100% | 100% | 0% | 98% | 10% | 0% | 0% | 1.0 |
| Aura | 6 | 100% | 100% | 100% | 100% | 0% | 0% | 83% | 0% | 0% | 1.0 |
| Creature + Equipment | 5 | 100% | 100% | 100% | 100% | 100% | 0% | 0% | 20% | 100% | 0.8 |

## Numeric stats

| Stat | Cards | Min | Median | Mean | Max |
|---|---|---|---|---|---|
| Cost | 721 | 0 | 3 | 3.73 | 10 |
| Influence | 721 | 0 | 3 | 3.22 | 13 |

**Cost curve:** 0: 23, 1: 100, 2: 148, 3: 123, 4: 99, 5: 64, 6: 53, 7: 52, 8: 22, 9: 22, 10: 15

**Influence curve:** 0: 176, 1: 65, 2: 95, 3: 89, 4: 102, 5: 53, 6: 40, 7: 40, 8: 16, 9: 13, 10: 11, 11: 5, 12: 9, 13: 7

## Aura Enhanceable

| Value | Cards | Share |
|---|---|---|
| No | 508 | 70% |
| Yes | 213 | 30% |

## Allied Auras

40 cards, 6 distinct values.

| Value | Cards | Share |
|---|---|---|
| Fire | 13 | 2% |
| Earth | 13 | 2% |
| Water | 13 | 2% |
| Air | 13 | 2% |
| Lightning | 13 | 2% |
| Dark | 5 | 1% |

## Keywords

150 cards, 6 distinct values.

| Value | Cards | Share |
|---|---|---|
| Soar | 39 | 5% |
| Overwhelm | 38 | 5% |
| Duel | 28 | 4% |
| Destruction | 28 | 4% |
| Discover | 21 | 3% |
| Gigantic | 8 | 1% |

## Subtype

152 cards, 3 distinct values.

| Value | Cards | Share |
|---|---|---|
| Unique | 126 | 17% |
| Starter | 24 | 3% |
| Token | 2 | 0% |

## Traits

482 cards, 28 distinct values.

| Value | Cards | Share |
|---|---|---|
| Cryptid | 252 | 35% |
| Myth | 165 | 23% |
| Terror | 135 | 19% |
| Aerial | 82 | 11% |
| Elemental | 82 | 11% |
| Beast | 79 | 11% |
| Ward | 75 | 10% |
| Anomaly | 62 | 9% |
| Hybrid | 55 | 8% |
| Trickster | 45 | 6% |
| Location | 39 | 5% |
| Aquatic | 34 | 5% |
| Dragon | 32 | 4% |
| Spectral | 25 | 3% |
| Afflicted | 24 | 3% |
| Nocturnal | 17 | 2% |
| Magical | 14 | 2% |
| Shapeshifter | 13 | 2% |
| Machina | 12 | 2% |
| Headless | 12 | 2% |
| Landmark | 11 | 2% |
| Glacial | 10 | 1% |
| Weather | 9 | 1% |
| Lucky | 2 | 0% |
| Fruit | 1 | 0% |
| Anomlay | 1 | 0% |
| Areial | 1 | 0% |
| Bodyless | 1 | 0% |

## Abilities

**Abilities per card:** 0: 59, 1: 631, 2: 31

59 cards have no abilities. 436 cards carry flavor text, and 148 have a variant subtitle (e.g. "At The Ready").

### Ability kinds

| Kind | Abilities |
|---|---|
| Triggered (On / When / While / If ...) | 257 |
| Static / one-shot effect | 202 |
| Activated (pay a cost: effect) | 183 |
| Keyword-led (Discover, Overwhelm, Duel ...) | 44 |
| Modal (Choose one) | 7 |

### Most common triggers (first 5 words)

| Trigger | Abilities |
|---|---|
| On Play | 125 |
| On Mission Declaration | 18 |
| On Successful Mission | 13 |
| When Dispelled | 10 |
| On Mission Resolution | 10 |
| Once per round | 7 |
| During Mission Resolution | 4 |
| At the end of your | 4 |
| When any friendly creature Moves | 3 |
| When a friendly equipment in | 3 |
| When you win a Mission | 3 |
| While this is the only | 2 |
| When a creature Moves to | 2 |
| If you have 8 or | 2 |
| When a friendly Fire unit | 2 |
| When a friendly Earth unit | 2 |
| While there is a friendly | 2 |
| When you play a Terra | 2 |
| During Missions | 2 |
| When a friendly Lightning unit | 2 |

### Most common activation costs (numbers shown as N)

| Cost | Abilities |
|---|---|
| [Tap this card] | 28 |
| [Tap N Fire Aura] | 26 |
| [Tap N Earth Aura] | 21 |
| [Tap N Air Aura] | 18 |
| [Tap N Water Aura] | 16 |
| [Tap N Lightning Aura] | 12 |
| [Activated] | 12 |
| [Tap N Dark Aura] | 11 |
| Discard a Card | 9 |
| Sacrifice a Unit | 5 |
| [Either player may use this ability.] | 3 |
| Sacrifice This Equipment | 3 |
| Tap All of Your Untapped Aura | 2 |
| Sacrifice a Token | 2 |
| [Tap N Fire Aura] [Tap N Lightning Aura] | 1 |

### Capitalized game terms in rules text

Capitalized words are usually defined game actions or keywords.

| Term | Mentions |
|---|---|
| Tap | 165 |
| On Play | 130 |
| Influence | 120 |
| Hex | 77 |
| Spark | 72 |
| Move | 69 |
| Aura | 69 |
| Shatter | 46 |
| Mission | 41 |
| Sacrifice | 41 |
| Overwhelm | 38 |
| Deal | 35 |
| Missions | 35 |
| Choose | 34 |
| Fire Aura | 28 |
| On Mission | 28 |
| Gain | 26 |
| Duel | 25 |
| Put | 25 |
| Return | 25 |
| Earth Aura | 24 |
| Terra | 23 |
| Create | 23 |
| Jetsam | 23 |
| Discover | 22 |
| Draw | 21 |
| Card | 21 |
| Air Aura | 20 |
| Destruction | 19 |
| Sacrificed | 19 |
| Declaration | 18 |
| Water Aura | 18 |
| Discard | 18 |
| Soar | 16 |
| Activated | 16 |
| Declare | 15 |
| Lightning Aura | 15 |
| Influence Lightning | 15 |
| Dark Aura | 15 |
| On Successful | 14 |

## Design signals

### Creature stat rate: Influence per Cost, vanilla vs cards with abilities

The gap is the Influence MetaZoo charges for an ability (the "ability tax").

| Cost | Vanilla Influence | With abilities | Ability tax |
|---|---|---|---|
| 0 | 1.0 (n=2) | - | - |
| 1 | 1.9 (n=9) | 1.4 (n=28) | +0.5 |
| 2 | 2.4 (n=9) | 2.4 (n=54) | +0.0 |
| 3 | 4.6 (n=5) | 3.1 (n=63) | +1.5 |
| 4 | 5.0 (n=9) | 3.8 (n=53) | +1.2 |
| 5 | 6.8 (n=6) | 4.7 (n=39) | +2.1 |
| 6 | 7.2 (n=4) | 6.1 (n=38) | +1.2 |
| 7 | 9.0 (n=3) | 6.4 (n=41) | +2.6 |
| 8 | 10.2 (n=4) | 9.5 (n=15) | +0.7 |
| 9 | 11.0 (n=1) | 8.4 (n=20) | +2.6 |
| 10 | - | 6.1 (n=14) | - |

### Average Cost by rarity

| Rarity | Avg Cost |
|---|---|
| Common | 2.66 |
| Uncommon | 2.76 |
| Rare | 3.63 |
| Super Rare | 5.84 |
| Alt Art | 5.76 |
| Legend | 4.07 |
| Hidden | 5.32 |

### Aura identity (each Aura's "color pie")

Top keywords, traits and rules-text verbs per Aura.

| Aura | Keywords | Traits (excl. Cryptid/Myth) | Rules-text verbs |
|---|---|---|---|
| Air | Soar (27), Duel (8), Discover (5) | Aerial (46), Terror (31), Ward (18) | Move (60), Tap (27), Mission (19) |
| Earth | Duel (20), Overwhelm (13), Discover (4) | Beast (34), Ward (27), Hybrid (19) | Tap (31), Duel (22), Mission (14) |
| Fire | Destruction (8), Overwhelm (8), Discover (6) | Elemental (35), Terror (28), Beast (22) | Tap (27), Shatter (21), Mission (12) |
| Lightning | Overwhelm (6), Discover (2), Destruction (2) | Anomaly (22), Terror (22), Elemental (21) | Spark (41), Tap (22), Sacrifice (19) |
| Water | Overwhelm (7), Gigantic (4), Discover (3) | Aquatic (26), Ward (17), Terror (17) | Tap (31), Return (21), Mission (16) |
| Dark | Destruction (13), Gigantic (2), Overwhelm (1) | Terror (21), Afflicted (18), Nocturnal (14) | Mission (33), Hex (31), Tap (14) |

## Data quirks

- Some Trait values are misspelled in MetaZoo's own data (e.g. `Anomlay`, `Areial`) and are counted separately.
- A few rules texts contain garbled characters (e.g. `ÃÂ¥` where a bullet should be). That is in the official site's data, not introduced by the scraper.

## Artists

89 distinct artists.

| Artist | Cards |
|---|---|
| Sonderflex | 48 |
| Lillie McKay | 38 |
| Dao Le | 37 |
| Poncho | 33 |
| Kelsey Jachino | 26 |
| Jett Yates | 24 |
| Gamon Studio | 22 |
| Twin Ngo | 20 |
| Quentin Regnes | 17 |
| Fran P. Lobato | 17 |
| Sebastian Botello | 16 |
| Ciko Kholil | 16 |
| Umeshu Lovers | 15 |
| Eduardo Francisco | 14 |
| Jorge Rodrigues | 14 |
