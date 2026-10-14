# After-game reports

Use the [shared report](templates/core.md) after every test, then append exactly one
[game-type module](#modules). The shared questions stay the same across projects
and builds; modules add details needed to interpret a particular game. These are
reporting tools, not rules or approved mechanics. For Dark Charterlands, start with
the [TCG module](templates/tcg.md). The current [core-loop draft](../design/core-gameplay-loop.md)
is exploratory: record which proposal was actually tested without describing it as
a shipped rule.

## Run a short debrief

1. **Before play:** write the test question and exact rules, card/set, charter or
   software-build identifiers. Record any deviations from those versions.
2. **During play:** note timestamps/turns, observable events, rulings, failures and
   evidence IDs. Keep player comments as attributed, anonymized quotations.
3. **Immediately after play:** ask each player to rate the five shared questions
   privately before group discussion. Ask neutral prompts: "What stood out?",
   "Where did you hesitate?", "What would you try next?" Invite a highlight and
   low point; do not suggest a fix in the question.
4. **Together:** compare the planned objective with what occurred. Ask what may
   explain the gap and what is worth sustaining or testing next. Let quieter
   players speak before debating causes. A player may pass on any question.
5. **After players leave:** write evidence-backed findings, then proposed
   changes in their own section. Assign a disposition of keep, revise, retest
   or cut to each proposal. A suggestion is not an adopted design decision.

Aim for a 10–15 minute debrief. If a session stops early, still record why. Use
"not observed" or "not applicable" rather than inventing data.

## Modules

- [TCG](templates/tcg.md) — decks, matchup, card revisions, draw and balance
- [Board game](templates/board-game.md) — setup, teach, turns and scores
- [RPG](templates/rpg.md) — scenes, table comfort and Stars and Wishes
- [Video game](templates/video-game.md) — build, reproduction and telemetry
- [Mobile/location-based](templates/mobile-location.md) — device, place, access and re-entry

## Save and compare reports

Copy the core template, append the selected module, and save the filled report
under [reports](reports/README.md). The suggested path is
reports/<game-slug>/<version-slug>/YYYY-MM-DD-session-NN.md. Keep immutable
completed reports for each tested version; a later retest gets a new report.
Use a repository commit SHA or release tag where possible, plus the human rules
version and card/set revision or build. If a game uses a local charter or variant,
record its exact revision too. Use stable finding IDs to connect a report to
a later retest. Keep names, precise GPS traces and other personal details out of
the repository unless players have agreed to publication.

## Source notes

These are pointers for method, not claims that this template is a validated
questionnaire:

- [Hunicke, LeBlanc and Zubek, MDA](https://users.cs.northwestern.edu/~hunicke/MDA.pdf)
  separates mechanics, observed dynamics and desired player experience.
- [Schell Games, playtest questions](https://schellgames.com/blog/the-definitive-guide-to-playtest-questions-for-video-game-playtesters)
  recommends neutral questions and capturing reactions during and after play.
- [Haider et al. (2022), miniPXI](https://research.tue.nl/en/publications/minipxi-development-and-validation-of-an-eleven-item-measure-of-t/)
  is an eleven-item digital-game instrument. Its reported validation is nuanced;
  the five shared ratings here are separate, informal questions. Use the
  published wording and scoring if a study opts into miniPXI.
- [Burn After Running, Stars and Wishes](https://burnafterrunningrpg.com/2022/01/07/stars-and-wishes-because-feedback-is-hard/)
  describes an RPG closing round of appreciated moments and wishes.
- [Koskinen et al. (2019)](https://link.springer.com/chapter/10.1007/978-3-030-15616-9_7)
  reports a qualitative Pokémon GO survey covering gameplay, sociability,
  location, context and negative events. It informs prompts in the mobile
  module; it does not validate this form.
