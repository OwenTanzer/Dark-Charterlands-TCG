# TCG design research

Research compiled to inform the core gameplay loop of Dark Charterlands. It draws
on four kinds of source:

1. Academic scholarship
2. Designer talks and YouTube
3. Other games and design writing
4. Our own analysis of the 721 official MetaZoo cards (`research/metazoo/FEATURES.md`)

A fifth section covers community-run formats (Commander and its leagues).

Each section ends with numbered **insights (I1, I2, ...)**. The design document
([`docs/design/core-gameplay-loop.md`](../design/core-gameplay-loop.md)) traces
every mechanic back to these insights.

**Our expectations for the game** (agreed 2026-10-03):

| Expectation | Target |
|---|---|
| Depth | Hardcore, high depth (Magic-level decisions) |
| Priority formats | **Booster draft** and **multiplayer free-for-all (3-4+ players)** first |
| Medium | Physical cards |
| Game length | 20-40 minutes |
| Community | Groups and stores should **write their own rules** for the group format, like store-run Commander leagues, with the game providing a **charter** framework that supports it |

---

## 1. Academic scholarship

### Luck, skill and multiplayer: *Characteristics of Games*
Elias, Garfield and Gutschera ([MIT Press, 2012](https://books.google.com/books/about/Characteristics_of_Games.html?id=QVP8AQAAQBAJ))
analyze games by number of players, luck versus skill, and reward for effort. The book
has dedicated chapters on multiplayer games (including kingmaking) and on
indeterminacy. Garfield's related talk, ["Luck in Games"](https://www.youtube.com/watch?v=av5Hf7uOu-o)
(ITU Copenhagen), argues luck isn't the opposite of depth. The real question is
*where* the randomness sits and whether skill can act on it.

### Mechanics, Dynamics, Aesthetics (MDA)
Hunicke, LeBlanc and Zubek's [MDA framework (2004)](https://users.cs.northwestern.edu/~hunicke/MDA.pdf)
separates the rules we write (mechanics), the behavior those rules produce at the table
(dynamics), and the feelings players get (aesthetics). Designers work M→D→A while
players experience A→D→M. That is why this design starts from the experience we want
and works backwards to rules.

### The multiplayer problems: kingmaking, turtling, leader bashing
Lewis Pulsipher's chapter "The Three-Player Problem" in *Tabletop: Analog Game
Design* (Costikyan & Davidson, 2011) names four failure modes of free-for-all
conflict games, [summarized here](https://www.skeletoncodemachine.com/p/three-player-problem):

- **Turtling:** only defending while others weaken each other.
- **Leader bashing:** everyone attacks whoever is ahead.
- **Sandbagging:** hiding how well you're doing to avoid being bashed.
- **Kingmaking:** a player who can't win decides who does.

Without a fixed end, leader bashing can make the game go on forever.

Mitigations from that chapter:
- hidden victory information
- low direct interaction
- "equilibrium" (no single action swings much)
- player elimination
- points for second place
- making it hard to target a single player

A 2024 Uppsala game-design thesis, [*Mitigating Kingmaking in Multiplayer Board Games*](https://www.diva-portal.org/smash/get/diva2:1876522/FULLTEXT01.pdf),
applies a design-patterns analysis (Björk & Holopainen) and concludes there is
**no universal fix**. Designers must find what *facilitates* kingmaking in their own
game and target those specific rules.

### Rarity versus power
Ham's ["Rarity and Power: Balance in Collectible Object Games"](https://gamestudies.org/1001/articles/ham)
(*Game Studies* 10:1, 2010) shows that limiting powerful cards by rarity is "more
problematic" than limiting them by cost, because it makes an unlevel playing field.
His recommended alternative, from Sanctum's expansion: the most efficient,
direct-to-victory effects go at **common**. Rares should be *specialized*: dramatic
in the right situation, but requiring expertise.

### Drafting as a research problem
[Ward et al., "AI solutions for drafting in Magic: the Gathering" (IEEE CoG 2021)](https://arxiv.org/pdf/2009.00655)
treats booster draft as a hard sequential-decision problem. Bots must weigh raw
card quality against color commitment and the signals in what is passed to them.
Their M19 draft dataset is public ([draftsim.com/draft-data](https://draftsim.com/draft-data)).
Drafting is a deep skill axis in its own right, which supports making the draft part
of the game rather than a preamble.

### Balancing card pools
[de Mesentier Silva et al., "Evolving the Hearthstone Meta" (2019)](https://arxiv.org/abs/1907.01623)
uses simulated agents to measure how changing individual cards shifts the matchup
landscape. A related survey, [*A Taxonomy of Collectible Card Games from a Game-Playing AI Perspective*](https://arxiv.org/html/2410.06299),
catalogs how CCGs differ: hidden information, resource models, and turn structure.
Both support building a simple simulator early to catch dominant strategies.

### Why people play card games
A survey of 856 players of Hearthstone and Eternal, ["Understanding online collectible card game players' motivations"](https://dl.acm.org/doi/10.1145/3292147.3292216),
found four motivation clusters:
- immersion seekers
- socializers
- competitors
- "smarty-pants" (players who enjoy mastery)

Eternal players reported higher satisfaction of autonomy and competence. Turkay's
["Collectible Card Games as Learning Tools" (2012)](https://www.sciencedirect.com/science/article/pii/S1877042812018666/pdf?md5=1b796402815a19d689cfa54e17ebbe4a&pid=1-s2.0-S1877042812018666-main.pdf)
identifies deckbuilding and the social layer as the main motivational drivers.

**Insights**
- **I1. Put randomness where skill can act on it.** For a hardcore audience, variance
  should come from *what's available* (draft packs, opponents' hidden choices), not
  from failing to function (resource screw, dead draws). (Garfield; Elias et al.)
- **I2. Design experience-first.** Name the feelings we want, then pick mechanics that
  produce the dynamics behind them. (MDA)
- **I3. Free-for-all needs targeted anti-kingmaking rules.** No single fix works. Use
  several together: partly hidden scoring, a fixed end, no elimination, limited targeting
  reach, and rewards for attacking the leader. (Pulsipher; Uppsala 2024)
- **I4. Gate power with cost and specialization, not rarity.** Efficient cards at common;
  rares are situational and high-skill. This matters especially in booster draft, where
  unequal packs otherwise decide games. (Ham 2010)
- **I5. The draft is a skill engine.** Commitment versus flexibility, signaling and
  hate-drafting are deep decisions that can carry a lot of the game's depth. (Ward et al. 2021)
- **I6. Serve competence and autonomy.** Mastery-driven players want visible skill
  expression and real choices. (OCCG motivation survey)

---

## 2. Designer talks and YouTube

> These are talks and videos from working TCG designers. Where a summary below is
> drawn from an accompanying article or secondary write-up rather than the video
> itself, that is noted.

- **Mark Rosewater, ["Twenty Years, Twenty Lessons" (GDC 2016)](https://gdcvault.com/play/1023186/Twenty-Years-Twenty)**,
  free on the GDC YouTube channel, with a [written version](https://magic.wizards.com/en/news/making-magic/twenty-years-twenty-lessons-part-1-2016-05-30).
  Lessons used here:
  - #1: fighting against human nature is a losing battle
  - #2: aesthetics matter
  - #3: resonance is important
  - #5: don't confuse "interesting" with "fun"
  - #6: understand what emotion your game is trying to evoke
  - Plus, from the same talk: "if everyone likes your game but no one loves it, it will fail."
- **Ben Brode, ["Designing MARVEL SNAP" (GDC 2023)](https://gdcvault.com/free/gdc-23/)**,
  from the Hearthstone and Marvel Snap lead designer. It is often cited for defining
  elegance as mechanics that give a lot of depth for little rules overhead (per a
  secondary summary). Snap's simultaneous reveal across contested locations is a proven
  model for fast, tense card games.
- **Richard Garfield, ["Luck in Games"](https://www.youtube.com/watch?v=av5Hf7uOu-o)**,
  and **Skaff Elias, "Luck and Skill in Games" (GDC Next 2013)**: how to blend
  luck and skill so outcomes feel earned while games stay replayable.
- **Steve Sekula, ["Designing TCG Resource Systems"](https://www.youtube.com/watch?v=JCKcYJTyHDA)**:
  the resource system is "arguably the most important design aspect" of a TCG because it
  decides how players actually play their cards. (Not summarized in detail here; it's
  recommended viewing before locking the resource rules.)
- **[TCG Design Theory video podcast](https://www.youtube.com/playlist?list=PLRMfaCJfWOsgejA1i51a95xW9kVQjsgAg)**:
  interviews with independent TCG creators. Useful for indie production and testing
  practice.
- **Caleb Gannon (Algomancy)**, a large MTG draft/limited YouTuber who built a TCG.
  His [design write-up](https://calebgannon.com/2023/07/08/the-making-of-algomancy/) is
  the single most relevant source for our brief, summarized in section 3.

> **Full video digest:** the 18 most-watched TCG design videos (Rosewater, Brode, Garfield, Slay the Spire, Pokémon, Hearthstone, Race for the Galaxy, Extra Credits and more) were run through our local Mistral pipeline. The result is 106 timestamped takeaways grouped by design area, in [`research/design-videos/DIGEST.md`](../../research/design-videos/DIGEST.md) ([PDF](../../research/design-videos/DIGEST.pdf)).

**Insights**
- **I7. Work with human nature in multiplayer.** People avoid being seen as a threat
  and don't want to be the one who attacks. Give them *reasons* to act that aren't
  personal. (Rosewater lesson #1; Conspiracy, section 3)
- **I8. Interesting is not fun.** Every mechanic must earn its place in play, not just
  on paper. (Rosewater #5)
- **I9. Elegance: depth per rule.** A hardcore game should get its depth from how a few
  rules interact, not from a large rulebook. (Brode)
- **I10. The resource system is the foundation.** Decide it first and test it hardest.
  (Sekula)

---

## 3. Other games and design writing

### Algomancy: a TCG built around live drafting
Caleb Gannon's [write-up](https://calebgannon.com/2023/07/08/the-making-of-algomancy/)
lists goals almost identical to ours:
- Competitive depth with less randomness.
- **No waiting on opponents.** "In a 4 player game you have 4 players each thinking
  for 5 minutes ... 15 of which you have to sit and wait."
- Works at any player count.
- Interaction-centered, not "multiplayer solitaire".
- **The draft continues through the whole game**, because the draft is usually the
  most fun part of cube.

His key decisions after months of playtesting:
- **Live draft replaces the draw step.** Each turn you combine your hand with the pack
  and take cards until a fixed number remain. This ended dead cards and let players
  pivot.
- **Packs are fully replenished every few turns** so drafting stays fresh.
- **Planning happens in parallel** (like 7 Wonders), and interaction gets its own
  ordered window with an **initiative** holder who must act first.
- **Play cards *after* combat, not before**, so plans made during the draft hold up and
  defensive interaction isn't telegraphed.
- **Resources are drafted:** you spend a card from hand to take a resource, so there's
  no resource screw. A free bonus resource for staying in one faction rewards commitment.
- **Multiplayer scales through local interaction only.** You fight only your left and
  right neighbors, in isolated "regions", so all combats resolve in parallel and game
  length barely grows with player count.
- **Snowballing is the cost of low randomness.** The fix is specific, high-reward
  comeback cards and very careful balance.
- **Sold in complete sets**, so a balance mistake (or ban) doesn't cost players money.

### 7 Wonders and simultaneous drafting
In 7 Wonders all players pick from their hand and pass at the same time. Because
"everyone chooses at the same time, turns stay fast even" at high player counts
([overview](https://boardgamearchive.com/games/7-wonders/)). The cost is low
interaction, which Algomancy and Snap-style contested locations address.

### Conspiracy: Magic's multiplayer draft set
Magic's two *Conspiracy* sets were built for exactly our two priority formats: booster
draft *and* multiplayer ([Rosewater, "It's Another Conspiracy"](https://magic.wizards.com/en/news/making-magic/its-another-conspiracy-2016-08-15)).
The diagnosis: multiplayer's main weakness is that "being seen as a threat leads you
to facing multiple other players", so the correct play is to turtle, which "leads to
slow, non-interactive games."

The fixes:
- **Dethrone:** a bonus for attacking the leader, which is both a catch-up mechanism and
  a non-personal excuse to attack.
- **Monarch:** a single stealable title that draws a card every turn, "drawing
  bullseyes" so players fight over it. Its reward had to be immediate, or the holder
  turtled.
- **Melee:** rewards attacking *different* players.
- **Goad:** forces creatures to attack someone else.
- **Draft-matters cards:** cards that affect the draft itself. They worked better once
  they were tied to a color, so they flowed to the players who would use them.

### Limited set structure
Rosewater's [Nuts & Bolts #12: Limited themes](https://magic.wizards.com/en/news/making-magic/nuts-bolts-12-part-2-limited-themes-2020-03-16)
gives the house formula for draft sets:
- About **three major themes** per set.
- **Ten draft archetypes**, one per two-color pair, each usually announced by a
  "signpost" uncommon.
- An expected spread of mono-, two- and three-color decks, which determines how much
  color fixing to print.
- Themes need enough **as-fan** (expected copies per pack) to be draftable.

### Commander politics
In Commander, Magic's most popular multiplayer format, threat assessment,
diplomacy and timing are core skills ([Star City Games, "The Politics of Commander"](https://articles.starcitygames.com/magic-the-gathering/select/the-politics-of-commander/)).
High life totals make deterrence and alliance-building viable strategies. Politics
can be *depth* rather than a flaw if the rules channel it.

**Insights**
- **I11. Simultaneous phases are how a deep game stays under 40 minutes with 4 players.**
  Planning, drafting and card play happen in parallel. Only real interaction is
  sequenced, under an initiative rule. (Algomancy; 7 Wonders)
- **I12. Make the draft live.** Drafting during the game merges our two priorities
  (booster draft plus multiplayer) into one experience and removes dead draws.
  (Algomancy; Conspiracy)
- **I13. Local interaction scales.** Neighbor-only fights resolve in parallel. One
  *shared* contested objective gives the table a common focus and a built-in
  leader-check. (Algomancy regions; Snap locations; Monarch)
- **I14. Give players non-personal reasons to attack, especially the leader.**
  (Dethrone, Monarch, Melee, Goad)
- **I15. Use the draft-set structure:** about 3 themes, 10 two-faction archetypes with
  signposts, and enough as-fan. (Nuts & Bolts #12)
- **I16. Low randomness means snowballing.** Plan for comeback tools and a fixed end
  from day one. (Algomancy; Pulsipher)
- **I17. Sell complete sets.** Balance can then be fixed cheaply, and power isn't
  locked behind rarity. (Algomancy; Ham)

---

## 4. What our MetaZoo analysis tells us

MetaZoo is the closest published game to the lane/mission structure we're considering,
so we scraped all 721 official cards (`research/metazoo/`). The full numbers are in
`FEATURES.md`. The findings that matter for design:

- **A lane game built on Influence, not damage.** Units contribute **Influence** to
  win **Missions** in lanes. Units **Move** between lanes. The most common triggers
  are On Play, On Mission Declaration and On Successful Mission. Nothing has to "die"
  to make progress, which is useful for a free-for-all where elimination is
  undesirable (I3).
- **A clean stat rate.** A vanilla creature gets roughly **Cost + 1-2 Influence**.
  Cards with abilities pay an **"ability tax" of about 1.2-2.6 Influence** at Cost 3-9.
  This gives us a starting costing formula to tune from.
- **Power is gated by cost more than rarity.** Average Cost runs Common 2.7, Rare 3.6,
  Super Rare 5.8. That's directionally what Ham recommends (I4), though MetaZoo still
  puts many top cards at Super Rare.
- **Six Auras with crisp identities.** Each Aura owns one or two verbs:
  - Air: Move, Soar
  - Earth: Duel, big Beasts
  - Fire: Shatter, Destruction
  - Lightning: Spark tokens, Sacrifice
  - Water: Return (bounce)
  - Dark: Hex counters, Mission manipulation

  That's a working "color pie", which draft needs (I15).
- **Few keywords, many traits.** Only 6 keywords against 28 traits. Traits are tribal
  hooks; keywords are mechanics. That's a reasonable complexity budget for commons.
- **Most costs tap Aura.** Activated abilities are dominated by `[Tap N <Aura> Aura]`
  and `[Tap this card]`. The Aura zone does double duty as mana and as an ability
  budget, which adds depth without adding rules (I9).
- **Data hygiene matters.** MetaZoo's own data has misspelled traits and garbled text.
  A small reminder to keep our card database clean and machine-readable from the start.

**Insights**
- **I18. Contest Influence, not life totals.** A lane/mission structure where you win
  locations by Influence avoids player elimination and invites the whole table into
  every contest.
- **I19. Start from MetaZoo's costing:** about Cost + 1.5 Influence for vanilla units,
  minus about 1.5-2 per ability. Then tune by playtest.
- **I20. One or two signature verbs per faction**, a modest keyword count, and traits as
  the main source of synergy.

---

## 5. Community-run formats and house rules

### Commander: a format the community built
Commander began as **Elder Dragon Highlander**, a fan-made format Adam Staley
developed for his local playgroups in Alaska in the late 1990s. From 2006 its banned
list was kept by a volunteer **Commander Rules Committee**, not by Wizards of the
Coast ([Wikipedia](https://en.wikipedia.org/wiki/Magic:_The_Gathering_Commander);
[MTG Wiki](https://mtg.fandom.com/wiki/Commander_(format))). It grew into Magic's most
popular multiplayer format. In **September 2024**, after an extreme backlash to a
banning decision, the committee **dissolved and handed the format to Wizards**
([Commander's Herald](https://commandersherald.com/commander-rules-committee-dissolves/)).

### Rule 0 and the need for a shared vocabulary
Before 2025, groups set expectations with an informal pregame **"Rule 0"**
conversation, rating decks on a subjective 1-10 scale where "almost every homebrew
deck was inexplicably described as a 7 out of 10". In February 2025 Wizards introduced
**Commander Brackets**: five clearly defined, intent-based tiers plus a "Game
Changers" list ([MTG Wiki: Commander Brackets](https://mtg.wiki/page/Commander_Brackets);
[Draftsim](https://draftsim.com/mtg-commander-format-panel/)).

### Store leagues
Stores run their own Commander leagues with their own scoring: **league points,
achievements, participation prizes**, and pods seated by standings
([WPN: running Commander events](https://wpn.wizards.com/en/news/how-to-run-successful-commander-events-and-grow-your-community);
[EDHREC: creating an EDH league](https://edhrec.com/articles/bringing-magic-to-life-creating-an-edh-league);
[r/EDH store point systems](https://www.reddit.com/r/EDH/comments/7yrt5l/anyones_local_game_store_do_some_sort_of_point/)).
Wizards now packages this as **"Commander Nights"**, a weekly league with
*rotating global rules* and achievement-based prizes ([WPN](https://wpn.wizards.com/en/news/managing-wpn-programs)).
Third-party league software lets organizers set their own scoring and season length
([example](https://mtgsl.cloud/)).

### Community stewardship
When Fantasy Flight ended Android: Netrunner, the community founded **Null Signal
Games**, a registered nonprofit that keeps designing and supporting the game,
including help for local organizers ([nullsignal.games](https://nullsignal.games/);
[Sprites & Dice](https://spritesanddice.com/features/project-nisei-and-future-netrunner/)).

**Insights**
- **I21. Communities make formats; publishers should give them tools, not just
  permission.** Commander grew from house rules into Magic's biggest multiplayer
  format. We should design for that from day one.
- **I22. Ship a shared vocabulary for expectations.** Unstructured Rule 0 produced
  "everything is a 7". Brackets fixed it with defined tiers. Groups need common terms
  for power level and house rules.
- **I23. Keep the core stable and make the edges modular.** Leagues thrive on rotating
  rules and achievements, while the Rules Committee's collapse shows the cost of
  contested central control. Fix the core rules, and make the parts communities change
  explicit, swappable "dials".
- **I24. Give stores a turnkey league kit:** scoring, achievements, seating by standings
  and season length, so running a league is easy.

---

## Insight index

| # | Insight | Main sources |
|---|---|---|
| I1 | Put randomness where skill can act on it | Garfield; Elias et al. |
| I2 | Design experience-first | MDA |
| I3 | Targeted anti-kingmaking rules | Pulsipher; Uppsala 2024 |
| I4 | Gate power by cost and specialization, not rarity | Ham 2010 |
| I5 | The draft is a skill engine | Ward et al. 2021 |
| I6 | Serve competence and autonomy | OCCG motivation survey |
| I7 | Work with human nature in multiplayer | Rosewater |
| I8 | Interesting is not fun | Rosewater |
| I9 | Depth per rule | Brode |
| I10 | The resource system is the foundation | Sekula |
| I11 | Simultaneous phases for 20-40 min at 4 players | Algomancy; 7 Wonders |
| I12 | Make the draft live | Algomancy; Conspiracy |
| I13 | Local interaction plus one shared objective | Algomancy; Snap; Monarch |
| I14 | Non-personal reasons to attack the leader | Conspiracy |
| I15 | Draft-set structure (themes, archetypes, as-fan) | Nuts & Bolts #12 |
| I16 | Plan for snowballing and a fixed end | Algomancy; Pulsipher |
| I17 | Sell complete sets | Algomancy; Ham |
| I18 | Contest Influence, not life totals | MetaZoo analysis |
| I19 | Start from MetaZoo's stat rate | MetaZoo analysis |
| I20 | Signature verbs per faction; traits for synergy | MetaZoo analysis |
| I21 | Give communities tools to make formats | Commander history |
| I22 | Ship a shared vocabulary for expectations | Rule 0 → Commander Brackets |
| I23 | Stable core, modular "dials" at the edges | Store leagues; Rules Committee |
| I24 | Turnkey league kit for stores | WPN Commander Nights; EDH leagues |
