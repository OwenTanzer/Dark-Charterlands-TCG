"""Transcribe a video that has no YouTube captions, locally with faster-whisper,
into the same "[mm:ss] text" line format the pipeline uses. run_pipeline.py then
summarizes it like any other video.

Run with a Python that has faster-whisper (e.g. donkeyballs/whisper-key-venv):
    <whisper-python> transcribe_local.py <audio_file> <out_txt> [--model small.en] [--device cpu]

Get the audio first, e.g.:
    yt-dlp -f bestaudio -x --audio-format mp3 -o "part1.%(ext)s" -- <video_id>
"""
import argparse
from pathlib import Path

from faster_whisper import WhisperModel


def stamp(sec: float) -> str:
    sec = int(sec)
    return f"[{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}]" if sec >= 3600 else f"[{sec // 60:02d}:{sec % 60:02d}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--model", default="small.en")
    ap.add_argument("--device", default="cpu", help="cpu keeps the GPU free for Ollama")
    args = ap.parse_args()

    model = WhisperModel(args.model, device=args.device, compute_type="int8" if args.device == "cpu" else "float16")
    segments, info = model.transcribe(str(args.audio), language="en", vad_filter=True)
    lines = [f"{stamp(s.start)} {s.text.strip()}" for s in segments if s.text.strip()]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {args.out}: {len(lines)} lines, {info.duration / 60:.1f} min of audio")


if __name__ == "__main__":
    main()
