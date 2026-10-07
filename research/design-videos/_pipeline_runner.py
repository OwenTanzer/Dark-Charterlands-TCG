"""Runs the media-flow-critique-youtube pipeline's run_single_video_ollama.main()
for one video, with memory-saving settings for a model larger than the GPU:

- smaller transcript pieces and context window (MAX_CHUNK_CHARS / NUM_CTX)
- use_mmap=false on every Ollama request, so system RAM holds only the layers
  that don't fit on the GPU instead of mapping the whole model file

Called by run_pipeline.py with the pipeline repo as the working directory:
    python _pipeline_runner.py <video_id> <model> <chunk_chars> <num_ctx> [local_transcript.txt]
"""
import os
import sys

import requests

sys.path.insert(0, os.getcwd())
import run_single_video_ollama as pipeline  # noqa: E402

_post = requests.post


def _post_without_mmap(url, *args, json=None, **kwargs):
    if isinstance(json, dict) and isinstance(json.get("options"), dict):
        json["options"]["use_mmap"] = False
    return _post(url, *args, json=json, **kwargs)


requests.post = _post_without_mmap

video_id, model, chunk_chars, num_ctx = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])

# Optional 5th argument: a local "[mm:ss] text" transcript (from transcribe_local.py)
# for videos with no YouTube captions. It replaces the pipeline's caption fetch.
if len(sys.argv) > 5:
    from pathlib import Path

    local_text = Path(sys.argv[5]).read_text(encoding="utf-8")

    def _local_transcript_body(vid):
        return pipeline.fetch_video_metadata(vid).title, local_text

    pipeline.build_transcript_body = _local_transcript_body

pipeline.MAX_CHUNK_CHARS = chunk_chars
pipeline.NUM_CTX = num_ctx
sys.argv = ["run_single_video_ollama.py", video_id, model]
pipeline.main()
