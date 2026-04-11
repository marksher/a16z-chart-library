#!/usr/bin/env python3
"""
Re-classify ALL images across every graphs/ subfolder using 15 parallel workers.

Two-tier output structure:
  Pure chart types (top-level):  bar  line  area  pie  scatter  table  map
  Everything else (other_v2/):   combo  infographic  title  screenshot  other

Coordination files (in progress/):
  .queue.txt       — master list of all images (written once at start)
  .in_progress.txt — appended as each image starts (lock-protected)
  .done.txt        — appended as each image finishes (lock-protected)
"""

import os
import sys
import base64
import shutil
import threading
import queue
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import io

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

load_dotenv(REPO_ROOT / ".env")

# ── Config ────────────────────────────────────────────────────────────────────
GRAPHS_DIR   = REPO_ROOT / "graphs"
PROGRESS_DIR = REPO_ROOT / "progress"
OTHER_V2_DIR = GRAPHS_DIR / "other_v2"
MODEL        = os.getenv("MODEL", "o4-mini")
NUM_WORKERS  = 15

QUEUE_FILE       = PROGRESS_DIR / ".queue.txt"
IN_PROGRESS_FILE = PROGRESS_DIR / ".in_progress.txt"
DONE_FILE        = PROGRESS_DIR / ".done.txt"

# Pure chart type folders (top-level)
CHART_TYPES = {"bar", "line", "area", "pie", "scatter", "table", "map"}

# other_v2 subtypes
OTHER_V2_TYPES = {"combo", "infographic", "title", "screenshot", "other"}

ALL_VALID = CHART_TYPES | OTHER_V2_TYPES

# Folders to scan (skip other_v2 and hidden files)
SOURCE_FOLDERS = list(CHART_TYPES) + list(OTHER_V2_TYPES - {"other"}) + ["other"]

PROMPT = """Look at this image carefully and classify it into exactly one category.

PURE CHART TYPES (top-level categories):
- bar        — bar chart or column chart
- line       — line chart or trend chart (no filled area)
- area       — area chart or stacked area chart (filled below line)
- pie        — pie chart or donut chart
- scatter    — scatter plot, bubble chart, dot plot, dumbbell/range chart
- table      — data table or grid of numbers/text
- map        — geographic or spatial map

OTHER VISUAL TYPES:
- combo      — chart mixing multiple types (e.g. bar+line dual-axis, map+chart inset)
- infographic — designed visual mixing text, icons, and data (not a single chart)
- title       — title card, banner, decorative header, or text-only image
- screenshot  — screenshot of an app, website, UI, or document

FALLBACK:
- other      — does not fit any category above

Reply with exactly ONE word from the list above. No explanation."""


# ── Thread-safe file writers ──────────────────────────────────────────────────
_write_lock = threading.Lock()

def append_line(path: Path, line: str):
    with _write_lock:
        with path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

# ── Progress counter ──────────────────────────────────────────────────────────
_counter_lock = threading.Lock()
_done_count = 0
_total = 0

def increment_done():
    global _done_count
    with _counter_lock:
        _done_count += 1
        return _done_count


# ── Setup ─────────────────────────────────────────────────────────────────────

def check_env():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("ERROR: OPENAI_API_KEY not set. Add it to .env")
        sys.exit(1)
    print(f"Model: {MODEL}  Workers: {NUM_WORKERS}")
    return key


def setup_dirs():
    PROGRESS_DIR.mkdir(exist_ok=True)
    OTHER_V2_DIR.mkdir(exist_ok=True)
    for sub in OTHER_V2_TYPES:
        (OTHER_V2_DIR / sub).mkdir(exist_ok=True)
    # Ensure all top-level chart dirs exist
    for t in CHART_TYPES:
        (GRAPHS_DIR / t).mkdir(exist_ok=True)


def dest_for(classification: str) -> Path:
    """Map a classification string to its destination directory."""
    c = classification.strip().lower()
    if c in CHART_TYPES:
        return GRAPHS_DIR / c
    if c in OTHER_V2_TYPES:
        return OTHER_V2_DIR / c
    # Unknown response → other_v2/other
    return OTHER_V2_DIR / "other"


def current_type(image_path: Path) -> str:
    """Return the folder name that currently holds this image."""
    parent = image_path.parent
    if parent.parent.name == "other_v2":
        return parent.name  # e.g. "combo"
    return parent.name      # e.g. "bar"


# ── Build queue ───────────────────────────────────────────────────────────────

def collect_images() -> list[Path]:
    images = []
    for folder_name in SOURCE_FOLDERS:
        folder = GRAPHS_DIR / folder_name
        if not folder.exists():
            continue
        for ext in ("*.png", "*.jpg", "*.jpeg"):
            images.extend(folder.glob(ext))
    # Also scan other_v2 subdirs in case script is re-run
    if OTHER_V2_DIR.exists():
        for sub in OTHER_V2_TYPES:
            subdir = OTHER_V2_DIR / sub
            if not subdir.exists():
                continue
            for ext in ("*.png", "*.jpg", "*.jpeg"):
                images.extend(subdir.glob(ext))
    return sorted(set(images))


# ── Classification ────────────────────────────────────────────────────────────

def to_b64_png(image_path: Path) -> str:
    img = Image.open(image_path)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.standard_b64encode(buf.getvalue()).decode()


def classify(client: OpenAI, image_path: Path) -> str:
    try:
        b64 = to_b64_png(image_path)
    except Exception as e:
        print(f"  [WARN] Cannot read {image_path.name}: {e}")
        return "other"

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_completion_tokens=500,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/png;base64,{b64}"}},
                    {"type": "text", "text": PROMPT},
                ],
            }],
        )
        result = response.choices[0].message.content.strip().lower()
        # Exact match first
        if result in ALL_VALID:
            return result
        # Partial match fallback
        for t in ALL_VALID:
            if t in result:
                return t
        return "other"
    except Exception as e:
        print(f"  [WARN] API error for {image_path.name}: {e}")
        return "other"


# ── Worker ────────────────────────────────────────────────────────────────────

def process_image(client: OpenAI, image_path: Path) -> dict:
    """Classify one image, move it if needed, return result dict."""
    old_type = current_type(image_path)

    # Mark in-progress
    append_line(IN_PROGRESS_FILE, str(image_path))

    # Classify
    new_type = classify(client, image_path)
    dest_dir = dest_for(new_type)
    dest_path = dest_dir / image_path.name

    # Move if needed (handle filename collisions)
    action = "ok"
    if dest_dir != image_path.parent:
        if dest_path.exists():
            # Avoid collision: append _dup suffix
            stem = image_path.stem
            suffix = image_path.suffix
            dest_path = dest_dir / f"{stem}_dup{suffix}"
        shutil.move(str(image_path), str(dest_path))
        action = "moved"

    n = increment_done()
    if n % 50 == 0 or n == _total:
        print(f"  [{n}/{_total}] {old_type}/{image_path.name} → {new_type} ({action})")

    # Record done
    append_line(DONE_FILE, f"{old_type}\t{image_path.name}\t{new_type}\t{action}")

    return {"old": old_type, "new": new_type, "action": action}


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    global _total

    api_key = check_env()
    setup_dirs()
    client = OpenAI(api_key=api_key)

    # Phase 1: collect all images
    print("Scanning graph folders...")
    images = collect_images()
    _total = len(images)
    print(f"Found {_total} images to process.\n")

    # Write queue file
    QUEUE_FILE.write_text("\n".join(str(p) for p in images) + "\n", encoding="utf-8")
    IN_PROGRESS_FILE.write_text("", encoding="utf-8")
    DONE_FILE.write_text("", encoding="utf-8")

    # Phase 2: classify in parallel
    print(f"Starting {NUM_WORKERS} parallel workers...\n")

    work_queue: queue.Queue = queue.Queue()
    for img in images:
        work_queue.put(img)

    results = []

    def worker():
        while True:
            try:
                img_path = work_queue.get_nowait()
            except queue.Empty:
                break
            result = process_image(client, img_path)
            results.append(result)
            work_queue.task_done()

    threads = [threading.Thread(target=worker) for _ in range(NUM_WORKERS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Phase 3: summary
    done_count = DONE_FILE.read_text().count("\n")
    print(f"\n{'='*50}")
    print(f"DONE — {done_count}/{_total} images processed")
    print()

    # Tally moves
    moves: dict[tuple[str, str], int] = {}
    stayed = 0
    for r in results:
        if r["action"] == "moved":
            key = (r["old"], r["new"])
            moves[key] = moves.get(key, 0) + 1
        else:
            stayed += 1

    if moves:
        print("Moves:")
        for (old, new), count in sorted(moves.items()):
            print(f"  {old:15s} → {new:15s}  {count}")
    print(f"\nVerified correct (no move): {stayed}")
    print(f"\n.done.txt lines: {done_count}")


if __name__ == "__main__":
    main()
