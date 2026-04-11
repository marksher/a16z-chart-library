#!/usr/bin/env python3
"""
Re-classify images in graphs/other/ into more specific types.

Expanded taxonomy beyond the original 6 buckets:
  Data charts:   bar, line, area, pie, scatter, table, combo, map
  Non-chart:     infographic, title, screenshot, other

Reads config from .env: OPENAI_API_KEY, MODEL
"""

import os
import sys
import time
import base64
import shutil
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import io

load_dotenv()

GRAPHS_DIR = Path("graphs")
OTHER_DIR = GRAPHS_DIR / "other"
MODEL = os.getenv("MODEL", "o4-mini")

# Expanded set — new directories will be created as needed
ALL_TYPES = [
    # data charts
    "bar", "line", "area", "pie", "scatter", "table", "combo", "map",
    # non-chart
    "infographic", "title", "screenshot",
    # keep-as-other
    "other",
]

PROMPT = """Look at this image carefully and classify it into exactly one category.

DATA CHART types (pick the best fit):
- bar      — bar chart or column chart
- line     — line chart or trend chart (no filled area)
- area     — area chart or stacked area chart (filled below line)
- pie      — pie chart or donut chart
- scatter  — scatter plot, bubble chart, dot plot, dumbbell/range chart
- table    — data table or grid of numbers/text
- combo    — chart mixing multiple types (e.g. bar+line, map+bar inset, bubble map)
- map      — geographic or spatial map, with or without data overlay

NON-CHART types:
- infographic  — designed visual mixing text, icons, and data (not a single chart)
- title        — title card, banner, decorative header, or text-only image with no data
- screenshot   — screenshot of an app, website, UI, or document

FALLBACK:
- other        — does not fit any category above

Reply with exactly ONE word from the list above. No explanation."""


def check_env():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("ERROR: OPENAI_API_KEY not set. Add it to .env")
        sys.exit(1)
    print(f"Model: {MODEL}")
    return key


def setup_dirs():
    for t in ALL_TYPES:
        (GRAPHS_DIR / t).mkdir(exist_ok=True)


def to_b64_png(image_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(image_bytes))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.standard_b64encode(buf.getvalue()).decode()


def classify(client: OpenAI, image_path: Path) -> str:
    try:
        b64 = to_b64_png(image_path.read_bytes())
    except Exception as e:
        print(f"  [WARN] Could not read {image_path.name}: {e}")
        return "other"

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_completion_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64}"},
                        },
                        {"type": "text", "text": PROMPT},
                    ],
                }
            ],
        )
        result = response.choices[0].message.content.strip().lower()
        if result in ALL_TYPES:
            return result
        # partial match fallback
        for t in ALL_TYPES:
            if t in result:
                return t
        return "other"
    except Exception as e:
        print(f"  [WARN] API error for {image_path.name}: {e}")
        return "other"


def main():
    api_key = check_env()
    setup_dirs()
    client = OpenAI(api_key=api_key)

    images = sorted(OTHER_DIR.glob("*.png")) + sorted(OTHER_DIR.glob("*.jpg"))
    if not images:
        print("graphs/other/ is empty — nothing to reclassify.")
        return

    print(f"Reclassifying {len(images)} images from graphs/other/\n")

    moved = {t: 0 for t in ALL_TYPES}

    for i, img_path in enumerate(images, 1):
        print(f"[{i}/{len(images)}] {img_path.name}: ", end="", flush=True)
        chart_type = classify(client, img_path)
        print(chart_type)

        if chart_type != "other":
            dest = GRAPHS_DIR / chart_type / img_path.name
            shutil.move(str(img_path), str(dest))
            moved[chart_type] += 1
        else:
            moved["other"] += 1

        time.sleep(0.3)

    print("\n" + "=" * 40)
    print("RECLASSIFICATION DONE")
    for t, n in moved.items():
        if n:
            print(f"  {t:12s}: {n}")
    remaining = len(list(OTHER_DIR.glob("*.png"))) + len(list(OTHER_DIR.glob("*.jpg")))
    print(f"\n  {remaining} images remain in graphs/other/")


if __name__ == "__main__":
    main()
