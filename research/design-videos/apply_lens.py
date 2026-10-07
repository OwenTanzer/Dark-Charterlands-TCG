"""Stage 2: read each video's pipeline summary (summaries/<id>.json) through the
Dark Charterlands design brief with a local Mistral model, then compile DIGEST.md.

For every key point the pipeline extracted, the model says which design area it
informs and what it implies for our game, citing the point by index. Timestamps
and links are joined back in from the pipeline output, so the model can't
invent them. Points that don't apply to us are dropped.

Usage:
    python apply_lens.py                  # lens every summary not yet lensed, then build DIGEST.md
    python apply_lens.py --digest-only    # rebuild DIGEST.md from lens/ only
    python apply_lens.py --model mistral-nemo
    python apply_lens.py --set leandro    # a video set in its own subfolder
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
# Data folder: this folder for the main set, or HERE/<name> for a --set (e.g. leandro/).
DATA = HERE
SUMMARIES, LENS = DATA / "summaries", DATA / "lens"
OLLAMA_URL = "http://localhost:11434/api/chat"

AREAS = [
    "Draft & set structure",
    "Multiplayer & politics",
    "Resource system",
    "Costing & balance",
    "Luck & randomness",
    "Turn structure & pacing",
    "Card & mechanic design",
    "Onboarding & complexity",
    "Community, leagues & house rules",
    "Playtesting & metrics",
    "Business & distribution",
]

BRIEF = """DARK CHARTERLANDS: design brief (v0.1, under review)
Expectations:
- E1 hardcore, high-depth strategy
- E2 booster draft is the primary way to play
- E3 multiplayer free-for-all for 3-4+ players is the primary format
- E4 physical cards only
- E5 games take 20-40 minutes
- E6 communities and stores write their own house rules ("Community Charters":
  stable core rules plus swappable rule "dials", a Clause Library, power-level
  Standings, store League Kits with achievements called Deeds)
Core loop: 5 Seasons. Each Season:
1. MUSTER: live draft from packs passed around the table (swap cards between hand and pack);
   bank cards face-down as Seals (the resource).
2. COMMIT: secretly place units face-down at your Holding, your two border Marches
   (shared only with a neighbor), or the shared Crown.
3. CONTEST: simultaneous reveal; Marches resolve in parallel, then the Crown;
   highest Influence claims Renown; the Initiative holder acts first.
4. EDICTS: play one-shot Edicts, Holdings and Relics.
5. RECKONING: the Crown winner becomes Regent (immediate reward plus Initiative);
   taking the Crown from the Regent grants a Usurper bonus.
Hidden Secret Charter objectives are scored at the end; there is no player elimination.
Five factions give 10 two-faction draft archetypes. Costing starts from MetaZoo's rate:
Influence of about Cost + 1.5, minus about 1.5-2 per ability."""

SCHEMA = {
    "type": "object",
    "properties": {
        "takeaways": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "point_index": {"type": "integer"},
                    "area": {"type": "string", "enum": AREAS},
                    "implication": {"type": "string"},
                    "relevance": {"type": "string", "enum": ["high", "medium", "low"]},
                },
                "required": ["point_index", "area", "implication", "relevance"],
            },
        },
        "overall_lesson": {"type": "string"},
    },
    "required": ["takeaways", "overall_lesson"],
}

SYSTEM = f"""You are a senior trading card game designer advising a team. Their game:

{BRIEF}

You will get the key points a pipeline extracted from one game-design video, numbered.
For each point that genuinely informs this game, return a takeaway with:
- point_index: the number of the point you are using (only numbers that exist)
- area: the design area the POINT ITSELF is about. Decide this from the point's own
  topic before thinking about our game. Examples: a point about luck or variance is
  "Luck & randomness"; about costs, power level or curves, "Costing & balance"; about
  teaching or learning curves, "Onboarding & complexity"; about game length or turn order,
  "Turn structure & pacing"; about data or testing, "Playtesting & metrics".
  Use "Multiplayer & politics" ONLY if the point is about games with 3+ players or
  player-vs-player politics. Use "Community, leagues & house rules" ONLY if the point is
  about player communities, organized play, or players changing the rules.
- implication: 1-3 sentences on what the team should do, check, or avoid in Dark
  Charterlands because of it. Connect it to the part of our design the point is really
  about. Do not force a link to Community Charters or any other feature that the point
  doesn't concern. Never invent facts about the video beyond the given points.
- relevance: how much this changes decisions for THIS game. "high" only if it should
  directly shape a current design decision (expect a minority of points); "medium" if
  it's useful background; "low" if it's a loose connection.
Skip points that don't apply (for example, digital-only UI advice for this physical game,
or company history with no design lesson).
Also give overall_lesson: one sentence on the most important lesson of this video for the team.
Reply with JSON only."""


AREA_DEFINITIONS = {
    "Draft & set structure": "booster drafting, set skeletons, archetypes, pack contents, set themes",
    "Multiplayer & politics": "games with 3+ players, alliances, kingmaking, targeting the leader",
    "Resource system": "mana/energy/resources: how players get and spend the means to play cards",
    "Costing & balance": "card costs, power levels, curves, balancing cards and strategies, power creep",
    "Luck & randomness": "luck, variance, randomness, skill vs luck",
    "Turn structure & pacing": "turn order, first-player advantage, game length, tempo, downtime",
    "Card & mechanic design": "designing individual cards, keywords and mechanics; themes, resonance, flavor",
    "Onboarding & complexity": "teaching, learning curves, rules complexity, accessibility for new players",
    "Community, leagues & house rules": "player communities, organized play, leagues, players changing rules",
    "Playtesting & metrics": "playtesting, data, feedback, iteration process",
    "Business & distribution": "monetization, product formats, pricing, marketing, distribution",
}
CLASSIFY_SCHEMA = {
    "type": "object",
    "properties": {"areas": {"type": "array", "items": {
        "type": "object",
        "properties": {"index": {"type": "integer"}, "area": {"type": "string", "enum": AREAS}},
        "required": ["index", "area"]}}},
    "required": ["areas"],
}


def classify_areas(lensed: dict, model: str) -> dict:
    """Re-file each takeaway by what its point is about, judged from the point alone
    (no design brief in the prompt, so the brief's emphasis can't pull points toward it)."""
    defs = "\n".join(f"- {a}: {d}" for a, d in AREA_DEFINITIONS.items())
    items = "\n".join(f"[{i}] {t['main_point']} {t['explanation'][:300]}" for i, t in enumerate(lensed["takeaways"]))
    resp = requests.post(OLLAMA_URL, json={
        "model": model, "stream": False, "format": CLASSIFY_SCHEMA,
        "options": {"temperature": 0, "num_ctx": 8192, "use_mmap": False, "num_predict": 1500},
        "messages": [
            {"role": "system", "content": "Classify each numbered game-design point into the single design area "
             f"it is mainly about. Areas:\n{defs}\nReply with JSON only, one entry per point."},
            {"role": "user", "content": items},
        ],
    }, timeout=1200)
    resp.raise_for_status()
    for a in json.loads(resp.json()["message"]["content"]).get("areas", []):
        i = a.get("index")
        if isinstance(i, int) and 0 <= i < len(lensed["takeaways"]) and a.get("area") in AREAS:
            lensed["takeaways"][i]["area"] = a["area"]
    lensed["areas_reclassified"] = True
    return lensed


def ts(sec):
    if sec is None:
        return ""
    sec = int(sec)
    return f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}" if sec >= 3600 else f"{sec // 60}:{sec % 60:02d}"


def lens_video(meta: dict, summary: dict, model: str) -> dict:
    points = summary["points"]
    numbered = "\n\n".join(f"[{i}] {p['main_point']}\n{p['explanation']}" for i, p in enumerate(points))
    user = f"Video: {meta['title']} by {meta['speaker']}\nVideo summary: {summary['summary']}\n\nKey points:\n\n{numbered}"
    resp = requests.post(OLLAMA_URL, json={
        "model": model, "stream": False, "format": SCHEMA,
        "options": {"temperature": 0, "num_ctx": 8192, "use_mmap": False,
                    # cap output so one runaway answer can't grow without bound
                    "num_predict": 3000},
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
    }, timeout=2400)
    resp.raise_for_status()
    out = json.loads(resp.json()["message"]["content"])
    kept = []
    for t in out.get("takeaways", []):
        i = t.get("point_index")
        if isinstance(i, int) and 0 <= i < len(points) and t.get("area") in AREAS:
            p = points[i]
            kept.append({**t, "main_point": p["main_point"], "explanation": p["explanation"],
                         "timestamp_seconds": p.get("timestamp_seconds"), "importance": p.get("importance")})
    return {"video": meta, "summary": summary["summary"], "overall_lesson": out.get("overall_lesson", ""),
            "takeaways": kept, "model": model, "pipeline_model": summary.get("model")}


def link(meta, sec):
    return f"https://www.youtube.com/watch?v={meta['id']}" + (f"&t={int(sec)}s" if sec is not None else "")


def build_digest(videos: list[dict]) -> str:
    lensed = [json.loads(p.read_text(encoding="utf-8")) for v in videos if (p := LENS / f"{v['id']}.json").exists()]
    order = {"high": 0, "medium": 1, "low": 2}
    cfg_path = DATA / "set.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}
    if cfg.get("order") == "list":  # a series: keep the videos.json order (part 1, 2, ...)
        pos = {v["id"]: i for i, v in enumerate(videos)}
        video_key = lambda vid: pos[vid["id"]]
    else:  # a collection of talks: most-watched first
        video_key = lambda vid: -vid["views"]
    md = [f"# {cfg.get('title', 'TCG design videos: key points for Dark Charterlands')}", ""]
    if cfg.get("intro"):
        md += [cfg["intro"], ""]
    md += [f"{len(lensed)} of {len(videos)} videos processed. Each video was summarized by the "
          "media-flow-critique-youtube pipeline (`run_single_video_ollama.py`, mistral-small: timestamped, "
          "transcript-grounded key points), then read against the Dark Charterlands design brief by "
          "`apply_lens.py`, and each takeaway was filed into a design area from its own content (a separate "
          "pass without the brief, so the brief couldn't bias the filing). Timestamps link to the moment in the video.", "",
          "> **How to read this:** the key points are grounded in each video's transcript. The *For us* lines are a "
          "local model's suggestions for the team to weigh, not decisions. Some are generic, and a few suggest things "
          "our design deliberately avoids (for example, random events or more Seasons). Check anything that matters "
          "against the linked timestamp.", "",
          "Regenerate: `python run_pipeline.py && python apply_lens.py`.", ""]
    missing = [v for v in videos if not (LENS / f"{v['id']}.json").exists()]
    if missing:
        md += ["**Not processed** (no transcript or the pipeline failed): " +
               ", ".join(f"[{v['title']}](https://www.youtube.com/watch?v={v['id']})" for v in missing), ""]

    md += ["## Headline lesson per video", "", "| Video | Views | Lesson |", "|---|---|---|"]
    for L in sorted(lensed, key=lambda L: video_key(L["video"])):
        v = L["video"]
        md.append(f"| [{v['title']}](https://www.youtube.com/watch?v={v['id']}) ({v['speaker']}) | "
                  f"{v['views']:,} | {L['overall_lesson'].replace('|', '/')} |")
    md.append("")

    by_area = defaultdict(list)
    for L in lensed:
        for t in L["takeaways"]:
            by_area[t["area"]].append((L["video"], t))
    md += ["## Takeaways by design area", "",
           "Sorted by relevance to Dark Charterlands (high first). Low-relevance takeaways are in the per-video section only.", ""]
    for area in AREAS:
        items = sorted([x for x in by_area.get(area, []) if x[1]["relevance"] != "low"],
                       key=lambda x: (order[x[1]["relevance"]], video_key(x[0]), x[1]["timestamp_seconds"] or 0))
        if not items:
            continue
        md += [f"### {area}", ""]
        for v, t in items:
            md += [f"- **{t['main_point']}** ({t['relevance']}). [{v['speaker']}, {ts(t['timestamp_seconds'])}]"
                   f"({link(v, t['timestamp_seconds'])})",
                   f"    - *For us:* {t['implication']}"]
        md.append("")

    md += ["## Per video", ""]
    for L in sorted(lensed, key=lambda L: video_key(L["video"])):
        v = L["video"]
        md += [f"### [{v['title']}](https://www.youtube.com/watch?v={v['id']})", "",
               f"{v['speaker']} · {v['views']:,} views", "", f"**Summary:** {L['summary']}", "",
               f"**Lesson for us:** {L['overall_lesson']}", ""]
        for t in sorted(L["takeaways"], key=lambda t: t["timestamp_seconds"] or 0):
            md += [f"- [{ts(t['timestamp_seconds'])}]({link(v, t['timestamp_seconds'])}) **{t['main_point']}** "
                   f"*({t['area']}, {t['relevance']})*",
                   f"    - {t['explanation']}",
                   f"    - *For us:* {t['implication']}"]
        md.append("")
    return "\n".join(md)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="mistral-small")
    ap.add_argument("--digest-only", action="store_true")
    ap.add_argument("--redo", action="store_true", help="Re-lens videos that already have lens output")
    ap.add_argument("--only", default=None, help="Comma-separated video ids to lens")
    ap.add_argument("--reclassify", action="store_true",
                    help="Only re-file existing takeaways into design areas, then rebuild the digest")
    ap.add_argument("--set", default=None, help="Video set subfolder, e.g. leandro (default: this folder)")
    args = ap.parse_args()
    global DATA, SUMMARIES, LENS
    DATA = HERE / args.set if args.set else HERE
    SUMMARIES, LENS = DATA / "summaries", DATA / "lens"
    videos = json.loads((DATA / "videos.json").read_text(encoding="utf-8"))
    LENS.mkdir(exist_ok=True)

    if args.reclassify:
        for v in videos:
            path = LENS / f"{v['id']}.json"
            if not path.exists() or (args.only and v["id"] not in args.only.split(",")):
                continue
            lensed = json.loads(path.read_text(encoding="utf-8"))
            if not lensed["takeaways"]:
                continue
            print(f"reclassify: {v['title']}", flush=True)
            try:
                lensed = classify_areas(lensed, args.model)
            except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
                print(f"    FAILED: {e}", file=sys.stderr)
                continue
            path.write_text(json.dumps(lensed, indent=2, ensure_ascii=False), encoding="utf-8")
        (DATA / "DIGEST.md").write_text(build_digest(videos), encoding="utf-8")
        print("wrote DIGEST.md")
        return

    if not args.digest_only:
        for v in videos:
            if args.only and v["id"] not in args.only.split(","):
                continue
            src, dest = SUMMARIES / f"{v['id']}.json", LENS / f"{v['id']}.json"
            if not src.exists() or (dest.exists() and not args.redo):
                continue
            print(f"lens: {v['title']}", flush=True)
            try:
                result = lens_video(v, json.loads(src.read_text(encoding="utf-8")), args.model)
            except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
                print(f"    FAILED: {e}", file=sys.stderr)
                continue
            dest.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            # free the model between videos so memory doesn't build up (see run_pipeline.py)
            requests.post("http://localhost:11434/api/generate", json={"model": args.model, "keep_alive": 0}, timeout=60)
            print(f"    {len(result['takeaways'])} takeaways", flush=True)

    (DATA / "DIGEST.md").write_text(build_digest(videos), encoding="utf-8")
    print("wrote DIGEST.md")


if __name__ == "__main__":
    main()
