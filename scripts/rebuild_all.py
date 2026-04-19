#!/usr/bin/env python3
"""
Rebuild everything: re-run all examples, rebuild all galleries,
update the examples README gallery table, and visually validate
all PNG/SVG outputs for clipping or alignment errors.

Usage:
    python scripts/rebuild_all.py
    python scripts/rebuild_all.py --check-only   # skip rebuild, just validate outputs
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"
VENV_PYTHON = REPO_ROOT / "venv" / "bin" / "python"

# All chart types in the library
CHART_TYPES = [
    "bar", "line", "area", "scatter", "pie", "table", "map",
    "diverging_bar", "sparkline_line", "sparkline_area", "sparkline_bar",
    "stat_card", "big_number", "gauge",
]

# Output stems that differ from the .py name
OUTPUT_STEMS = {"bar": "bar_stacked"}


# ── Discovery ────────────────────────────────────────────────────────────────

def discover_themes() -> list[str]:
    """Find all theme directories under examples/ that have at least one .py."""
    themes = []
    for d in sorted(EXAMPLES_DIR.iterdir()):
        if d.is_dir() and list(d.glob("*.py")):
            themes.append(d.name)
    return themes


# ── Phase 1: Run all examples ────────────────────────────────────────────────

def run_examples(themes: list[str]) -> list[str]:
    """Run every example .py for every theme. Returns list of errors."""
    python = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable
    errors = []

    for theme in themes:
        theme_dir = EXAMPLES_DIR / theme
        print(f"\n{'='*60}")
        print(f"  THEME: {theme}")
        print(f"{'='*60}")

        for chart in CHART_TYPES:
            py_file = theme_dir / f"{chart}.py"
            if not py_file.exists():
                errors.append(f"MISSING: {theme}/{chart}.py")
                print(f"  MISSING  {chart}.py")
                continue

            result = subprocess.run(
                [python, str(py_file)],
                capture_output=True, text=True, cwd=str(REPO_ROOT),
            )
            if result.returncode != 0:
                errors.append(f"FAILED: {theme}/{chart}.py — {result.stderr.strip()[:120]}")
                print(f"  FAIL     {chart}.py — {result.stderr.strip()[:80]}")
            else:
                print(f"  OK       {chart}.py")

    return errors


# ── Phase 2: Rebuild galleries ───────────────────────────────────────────────

def rebuild_galleries(themes: list[str]) -> list[str]:
    """Run generate_all.py for each theme. Returns list of errors."""
    python = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable
    errors = []

    print(f"\n{'='*60}")
    print("  REBUILDING GALLERIES")
    print(f"{'='*60}")

    for theme in themes:
        # default uses the top-level generate_all.py
        if theme == "default":
            gen_path = EXAMPLES_DIR / "generate_all.py"
        else:
            gen_path = EXAMPLES_DIR / theme / "generate_all.py"

        if not gen_path.exists():
            errors.append(f"MISSING: {theme}/generate_all.py")
            print(f"  MISSING  {theme}/generate_all.py")
            continue

        result = subprocess.run(
            [python, str(gen_path)],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        if result.returncode != 0:
            errors.append(f"GALLERY FAILED: {theme} — {result.stderr.strip()[:120]}")
            print(f"  FAIL     {theme}/all.html")
        else:
            print(f"  OK       {theme}/all.html")

    # Rebuild index.html
    _rebuild_index(themes)

    return errors


def _rebuild_index(themes: list[str]):
    """Regenerate examples/index.html with all themes."""
    gallery_themes = [t for t in themes if (EXAMPLES_DIR / t / "all.html").exists()]
    rows = "\n".join(
        f'      <li><a href="{t}/all.html">{t}</a></li>'
        for t in gallery_themes
    )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Chart Library — Theme Gallery</title>
  <style>
    body {{ font-family: Georgia, serif; background: #F0EBE3; color: #1C2B3A; padding: 40px; }}
    h1 {{ font-size: 28px; margin-bottom: 24px; }}
    ul {{ list-style: none; padding: 0; }}
    li {{ margin-bottom: 12px; }}
    a {{ color: #7B1A2A; font-size: 18px; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <h1>Chart Library — All Themes</h1>
  <ul>
{rows}
  </ul>
</body>
</html>
"""
    index_path = EXAMPLES_DIR / "index.html"
    index_path.write_text(html)
    print(f"  OK       index.html ({len(gallery_themes)} themes)")


# ── Phase 3: Update examples/README.md ───────────────────────────────────────

def update_readme(themes: list[str]) -> list[str]:
    """Regenerate the galleries and chart types tables in examples/README.md."""
    readme_path = EXAMPLES_DIR / "README.md"
    if not readme_path.exists():
        return [f"MISSING: examples/README.md"]

    errors = []
    content = readme_path.read_text()

    # ── Update galleries table ───────────────────────────────────────────
    gallery_themes = [t for t in themes if (EXAMPLES_DIR / t / "all.html").exists()]
    gallery_rows = []
    for t in gallery_themes:
        gallery_rows.append(
            f"| **{t}** "
            f"| [Open preview](https://raw.githack.com/marksher/a16z-chart-library/main/examples/{t}/all.html) "
            f"| [Download HTML](https://raw.githubusercontent.com/marksher/a16z-chart-library/main/examples/{t}/all.html) |"
        )
    gallery_table = (
        "| Theme | Preview | Download |\n"
        "|-------|---------|----------|\n"
        + "\n".join(gallery_rows)
    )

    # Replace the existing gallery table
    pattern = r"\| Theme \| Preview \| Download \|.*?(?=\n\n)"
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, gallery_table, content, count=1, flags=re.DOTALL)
    else:
        errors.append("Could not find gallery table in examples/README.md to update")

    # ── Update chart types table ─────────────────────────────────────────
    chart_names = {
        "bar": "Bar (stacked)", "line": "Line", "area": "Area",
        "scatter": "Scatter", "pie": "Pie", "table": "Table",
        "map": "Map", "diverging_bar": "Diverging Bar",
        "sparkline_line": "Sparkline Line", "sparkline_area": "Sparkline Area",
        "sparkline_bar": "Sparkline Bar", "stat_card": "Stat Card",
        "big_number": "Big Number", "gauge": "Gauge",
    }

    header = "| Chart | " + " | ".join(themes) + " |"
    sep = "|-------" + "|".join("-" * (len(t) + 2) for t in themes) + "|"
    rows = []
    for chart in CHART_TYPES:
        name = chart_names.get(chart, chart)
        cells = []
        for t in themes:
            py = EXAMPLES_DIR / t / f"{chart}.py"
            if py.exists():
                cells.append(f"[{chart}.py]({t}/{chart}.py)")
            else:
                cells.append("—")
        rows.append(f"| {name} | " + " | ".join(cells) + " |")

    chart_table = header + "\n" + sep + "\n" + "\n".join(rows)

    pattern = r"\| Chart \|.*?(?=\n\n---)"
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, chart_table, content, count=1, flags=re.DOTALL)
    else:
        errors.append("Could not find chart types table in examples/README.md to update")

    # ── Update regenerating section ──────────────────────────────────────
    regen_lines = []
    for t in themes:
        if t == "default":
            regen_lines.append(f"python examples/generate_all.py{' ' * max(1, 40 - len('python examples/generate_all.py'))}# {t}")
        else:
            cmd = f"python examples/{t}/generate_all.py"
            regen_lines.append(f"{cmd}{' ' * max(1, 40 - len(cmd))}# {t}")

    readme_path.write_text(content)

    print(f"\n{'='*60}")
    print("  UPDATED examples/README.md")
    print(f"{'='*60}")
    print(f"  Galleries: {len(gallery_themes)} themes")
    print(f"  Chart types: {len(CHART_TYPES)} × {len(themes)} themes")

    return errors


# ── Phase 4: Visual validation ───────────────────────────────────────────────

def validate_outputs(themes: list[str]) -> list[str]:
    """Check all PNG/SVG outputs for clipping, alignment, and content issues."""
    errors = []

    print(f"\n{'='*60}")
    print("  VISUAL VALIDATION")
    print(f"{'='*60}")

    for theme in themes:
        theme_dir = EXAMPLES_DIR / theme
        theme_errors = 0

        for chart in CHART_TYPES:
            stem = OUTPUT_STEMS.get(chart, chart)
            png_path = theme_dir / f"{stem}.png"
            svg_path = theme_dir / f"{stem}.svg"

            # ── PNG checks ───────────────────────────────────────────
            if not png_path.exists():
                errors.append(f"MISSING PNG: {theme}/{stem}.png")
                theme_errors += 1
                continue

            try:
                img = Image.open(png_path)
                w, h = img.size

                # Size check
                if w < 100 or h < 50:
                    errors.append(f"TOO SMALL: {theme}/{stem}.png ({w}×{h})")
                    theme_errors += 1

                # Blank check — image is all one color
                colors = img.getcolors(maxcolors=5)
                if colors is not None and len(colors) == 1:
                    errors.append(f"BLANK: {theme}/{stem}.png (single color)")
                    theme_errors += 1

                # Top-edge clipping check — if the top 3 pixel rows have
                # non-background content, title may be clipped
                if chart not in ("sparkline_line", "sparkline_area", "sparkline_bar",
                                 "stat_card", "big_number", "gauge"):
                    top_strip = img.crop((0, 0, w, 3))
                    top_colors = top_strip.getcolors(maxcolors=20)
                    if top_colors:
                        # Count pixels that aren't near the dominant color
                        dominant = max(top_colors, key=lambda x: x[0])[1]
                        non_bg = sum(
                            count for count, color in top_colors
                            if _color_dist(color, dominant) > 50
                        )
                        if non_bg > w * 0.1:  # more than 10% of top edge is content
                            errors.append(
                                f"CLIPPED TOP: {theme}/{stem}.png — content at top edge"
                            )
                            theme_errors += 1

                # Bottom-edge clipping check
                bottom_strip = img.crop((0, h - 3, w, h))
                bottom_colors = bottom_strip.getcolors(maxcolors=20)
                if bottom_colors:
                    dominant = max(bottom_colors, key=lambda x: x[0])[1]
                    non_bg = sum(
                        count for count, color in bottom_colors
                        if _color_dist(color, dominant) > 50
                    )
                    if non_bg > w * 0.15:
                        errors.append(
                            f"CLIPPED BOTTOM: {theme}/{stem}.png — content at bottom edge"
                        )
                        theme_errors += 1

            except Exception as e:
                errors.append(f"PNG ERROR: {theme}/{stem}.png — {e}")
                theme_errors += 1

            # ── SVG checks ───────────────────────────────────────────
            if not svg_path.exists():
                errors.append(f"MISSING SVG: {theme}/{stem}.svg")
                theme_errors += 1
                continue

            try:
                svg_text = svg_path.read_text()
                if "<svg" not in svg_text:
                    errors.append(f"INVALID SVG: {theme}/{stem}.svg — no <svg> tag")
                    theme_errors += 1
                if len(svg_text) < 500:
                    errors.append(f"TINY SVG: {theme}/{stem}.svg — {len(svg_text)} bytes")
                    theme_errors += 1
            except Exception as e:
                errors.append(f"SVG ERROR: {theme}/{stem}.svg — {e}")
                theme_errors += 1

        status = "OK" if theme_errors == 0 else f"{theme_errors} issues"
        print(f"  {theme}: {status}")

    return errors


def _color_dist(c1, c2) -> float:
    """Euclidean distance between two RGB(A) tuples."""
    return sum((a - b) ** 2 for a, b in zip(c1[:3], c2[:3])) ** 0.5


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Rebuild and validate all chart examples")
    parser.add_argument("--check-only", action="store_true",
                        help="Skip rebuild, just validate existing outputs")
    args = parser.parse_args()

    os.chdir(REPO_ROOT)
    themes = discover_themes()
    print(f"Discovered {len(themes)} themes: {', '.join(themes)}")

    all_errors = []

    if not args.check_only:
        all_errors += run_examples(themes)
        all_errors += rebuild_galleries(themes)
        all_errors += update_readme(themes)

    all_errors += validate_outputs(themes)

    # ── Summary ──────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    if all_errors:
        print(f"  DONE — {len(all_errors)} ISSUES FOUND:")
        print(f"{'='*60}")
        for e in all_errors:
            print(f"  • {e}")
        sys.exit(1)
    else:
        print(f"  DONE — ALL CLEAR")
        print(f"{'='*60}")
        print(f"  {len(themes)} themes × {len(CHART_TYPES)} chart types")
        print(f"  All PNGs non-blank, no clipping detected")
        print(f"  All SVGs valid")
        print(f"  examples/README.md updated")
        print(f"  examples/index.html updated")


if __name__ == "__main__":
    main()
