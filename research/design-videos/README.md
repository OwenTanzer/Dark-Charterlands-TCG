# TCG design videos → key points for Dark Charterlands

Runs the 18 most-watched TCG design talks and videos (`videos.json`, with YouTube
view counts as of 2026-10-05) through our local **media-flow-critique-youtube**
pipeline with **Mistral** (`mistral-small`), then reads every key point against the
Dark Charterlands design brief.

**Read the result:** [`DIGEST.md`](DIGEST.md) or [`DIGEST.pdf`](DIGEST.pdf). That's
106 takeaways with a headline lesson per video, grouped by design area, each linking
to its timestamp.

| Stage | Script | What it does |
|---|---|---|
| 1 | `run_pipeline.py` | Runs the pipeline's `run_single_video_ollama.py` once per video (through `_pipeline_runner.py`). The pipeline fetches the transcript and extracts timestamped, transcript-grounded key points with explanations. Writes `summaries/<id>.json`. Finished videos are skipped, so rerunning resumes. |
| 2 | `apply_lens.py` | Sends each video's points to Mistral with our design brief (E1-E6 and the core loop). For each point that informs our game it gets what it means for Dark Charterlands and how relevant it is. Points are cited by index and timestamps are joined back from stage 1, so links can't be invented. Writes `lens/<id>.json`. |
| 2b | `apply_lens.py --reclassify` | Files each takeaway into one of 11 design areas from the point's own text, with **no** design brief in the prompt. In a single pass, the brief pulled points toward whatever it emphasized (for example, filing luck points under multiplayer). |
| 3 | `apply_lens.py --digest-only` / `build_pdf.py` | Builds `DIGEST.md`, then prints it to `DIGEST.pdf` with headless Chrome or Edge. |

```
python run_pipeline.py
python apply_lens.py && python apply_lens.py --reclassify
python build_pdf.py
```

Requires Ollama with `mistral-small` and the pipeline repo at
`donkeyballs/media flow and critique youtube` (or set `MEDIA_FLOW_DIR`).

## Memory settings (12 GB GPU)
`mistral-small` (14 GB) doesn't fit on a 12 GB GPU, and the overflow ran the PC out
of RAM on hour-long talks. The scripts therefore:
- split transcripts into ~12,000-character pieces with an 8k context window
  (`--chunk-chars`, `--num-ctx`; the pipeline itself uses 30,000 / 16k)
- set `use_mmap: false`, so system RAM holds only the layers that don't fit on the GPU
- unload the model between videos
- cap each lens answer at 3,000 tokens

The first 8 videos were summarized with the pipeline's default 30k/16k settings, and
the other 10 with the smaller pieces.

## Caveats
- *For us* lines are a local model's suggestions, not decisions. Some are generic, and a
  few suggest things the design deliberately avoids (random events, more Seasons).
  Check anything important against the linked timestamp.
- The brief inside `apply_lens.py` mirrors `docs/design/core-gameplay-loop.md`. Update it
  when the design changes, then run `apply_lens.py --redo` followed by `--reclassify`.
