"""Render DIGEST.md to DIGEST.pdf (styled HTML printed by headless Chrome/Edge).

Usage:
    python build_pdf.py [--out path/to/file.pdf]
"""
import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent

CSS = """
@page { size: Letter; margin: 0.7in 0.75in; }
body { font-family: Georgia, 'Times New Roman', serif; font-size: 10.5pt; line-height: 1.45; color: #1d1d1f; }
h1 { font-size: 22pt; border-bottom: 3px solid #6b2737; padding-bottom: 6px; color: #3a1520; }
h2 { font-size: 15pt; color: #6b2737; margin-top: 26px; border-bottom: 1px solid #d8c9cc; padding-bottom: 3px; page-break-after: avoid; }
h3 { font-size: 12pt; color: #3a1520; margin-top: 18px; page-break-after: avoid; }
a { color: #1f4e8c; text-decoration: none; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; margin: 8px 0 14px; }
th, td { border: 1px solid #d8c9cc; padding: 4px 6px; vertical-align: top; text-align: left; }
th { background: #f3eced; }
tr { page-break-inside: avoid; }
li { margin: 3px 0; page-break-inside: avoid; }
li li { color: #444; }
code { font-family: Consolas, monospace; font-size: 9pt; background: #f4f4f4; padding: 0 3px; }
em { color: #5a3a40; }
"""


def find_browser() -> str:
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        shutil.which("chrome") or "", shutil.which("chromium") or "", shutil.which("google-chrome") or "",
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    raise SystemExit("No Chrome/Edge found for PDF printing.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "DIGEST.pdf")
    args = ap.parse_args()
    body = markdown.markdown((HERE / "DIGEST.md").read_text(encoding="utf-8"), extensions=["tables", "sane_lists"])
    html = f"<!doctype html><html><head><meta charset='utf-8'><title>Dark Charterlands: TCG design video digest</title><style>{CSS}</style></head><body>{body}</body></html>"
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "digest.html"
        page.write_text(html, encoding="utf-8")
        subprocess.run([find_browser(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={args.out.resolve()}", page.as_uri()],
                       check=True, capture_output=True, timeout=180)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
