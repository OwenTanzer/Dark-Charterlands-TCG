"""Stage 1: summarize every video in videos.json with the media-flow-critique-youtube
local pipeline (run_single_video_ollama.py, mistral-small by default).

The pipeline fetches each transcript, has the model extract timestamped key
points with explanations (citation-grounded against the transcript), and
writes summary_<id>_<model>.json in its own folder. This script runs it once
per video, skips videos already summarized, and copies results into
summaries/ here.

Usage:
    python run_pipeline.py                      # all videos, mistral-small
    python run_pipeline.py --model mistral-nemo
    python run_pipeline.py --only QHHg99hwQGY,HjhsY2Zuo-c
    python run_pipeline.py --chunk-chars 30000 --num-ctx 16384   # pipeline's own defaults

Long talks are split into ~12,000-character pieces with an 8k context window
(the pipeline itself uses 30,000 / 16k). That halves the model's working memory,
so mistral-small, which already spills past a 12 GB GPU, doesn't run the PC out of
RAM. The first 8 videos were done with the pipeline defaults.

Set MEDIA_FLOW_DIR if the pipeline repo isn't at ../../../media flow and critique youtube.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
PIPELINE = Path(os.environ.get(
    "MEDIA_FLOW_DIR", HERE.parents[2] / "media flow and critique youtube"))
OUT = HERE / "summaries"


def pipeline_python() -> str:
    venv = PIPELINE / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    return str(venv) if venv.exists() else sys.executable


def unload_model(model: str) -> None:
    """Free the model's memory between videos instead of letting it grow across the batch."""
    try:
        requests.post("http://localhost:11434/api/generate", json={"model": model, "keep_alive": 0}, timeout=60)
    except requests.RequestException:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="mistral-small")
    ap.add_argument("--only", default=None, help="Comma-separated video ids")
    ap.add_argument("--chunk-chars", type=int, default=12000,
                    help="Transcript piece size per model call (pipeline default 30000)")
    ap.add_argument("--num-ctx", type=int, default=8192,
                    help="Model context window per call (pipeline default 16384)")
    args = ap.parse_args()

    videos = json.loads((HERE / "videos.json").read_text(encoding="utf-8"))
    if args.only:
        wanted = set(args.only.split(","))
        videos = [v for v in videos if v["id"] in wanted]
    OUT.mkdir(exist_ok=True)
    slug = args.model.replace(":", "-").replace("/", "-")
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}

    for i, v in enumerate(videos, 1):
        dest = OUT / f"{v['id']}.json"
        if dest.exists():
            print(f"[{i}/{len(videos)}] skip (done): {v['title']}")
            continue
        print(f"[{i}/{len(videos)}] {v['title']}", flush=True)
        start = time.time()
        # Run the pipeline's own main() with memory-saving settings (see _pipeline_runner.py).
        proc = subprocess.run([pipeline_python(), str(HERE / "_pipeline_runner.py"), v["id"], args.model,
                               str(args.chunk_chars), str(args.num_ctx)],
                              cwd=PIPELINE, env=env, capture_output=True, text=True, encoding="utf-8")
        unload_model(args.model)
        produced = PIPELINE / f"summary_{v['id']}_{slug}.json"
        if proc.returncode == 0 and produced.exists():
            shutil.copy(produced, dest)
            n = len(json.loads(dest.read_text(encoding="utf-8"))["points"])
            print(f"    ok: {n} points in {(time.time() - start) / 60:.1f} min", flush=True)
        else:
            err = (proc.stderr or proc.stdout).strip().splitlines()[-3:]
            print(f"    FAILED: {' | '.join(err)}", flush=True)
            (OUT / f"{v['id']}.error.txt").write_text(proc.stderr + proc.stdout, encoding="utf-8")


if __name__ == "__main__":
    main()
