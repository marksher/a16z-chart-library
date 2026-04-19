#!/usr/bin/env python3
"""
Create a new chart-library theme from a website's colors and fonts.

Usage:
    python scripts/create_theme.py

Prompts for a URL, scrapes colors/fonts, generates:
  - themes/<name>/theme.yaml
  - scripts/chart_library/themes/<name>.yaml  (bundled copy)
  - examples/<name>/  (all chart examples + all.html gallery)

Then prints a preview link for the gallery.
"""

import colorsys
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Color extraction ─────────────────────────────────────────────────────────

HEX_RE = re.compile(r"#([0-9a-fA-F]{3,8})\b")
RGB_RE = re.compile(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)")
HSL_RE = re.compile(r"hsla?\(\s*([\d.]+)\s*,\s*([\d.]+)%\s*,\s*([\d.]+)%")


def _normalize_hex(h: str) -> str:
    """Normalize to 6-digit uppercase hex."""
    h = h.strip().upper()
    if len(h) == 3:
        h = h[0] * 2 + h[1] * 2 + h[2] * 2
    elif len(h) == 8:
        h = h[:6]  # strip alpha
    return f"#{h}"


def _rgb_to_hex(r, g, b):
    return f"#{int(r):02X}{int(g):02X}{int(b):02X}"


def _hsl_to_hex(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return _rgb_to_hex(r * 255, g * 255, b * 255)


def _hex_to_rgb(hex_color: str):
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _luminance(hex_color: str) -> float:
    r, g, b = _hex_to_rgb(hex_color)
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def _saturation(hex_color: str) -> float:
    r, g, b = _hex_to_rgb(hex_color)
    _, _, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return s


def _color_distance(c1: str, c2: str) -> float:
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5


def extract_colors(html: str, stylesheets: list[str]) -> list[str]:
    """Extract all color values from HTML and CSS, return sorted by frequency."""
    all_text = html + "\n".join(stylesheets)
    colors = Counter()

    for m in HEX_RE.finditer(all_text):
        h = m.group(1)
        if len(h) in (3, 6, 8):
            colors[_normalize_hex(h)] += 1

    for m in RGB_RE.finditer(all_text):
        colors[_rgb_to_hex(int(m.group(1)), int(m.group(2)), int(m.group(3)))] += 1

    for m in HSL_RE.finditer(all_text):
        colors[_hsl_to_hex(float(m.group(1)), float(m.group(2)), float(m.group(3)))] += 1

    # Filter out near-black, near-white, and grays (low saturation)
    # Keep them separate for background/text detection
    return [c for c, _ in colors.most_common()]


def extract_fonts(html: str, stylesheets: list[str]) -> list[str]:
    """Extract font-family declarations from HTML/CSS."""
    all_text = html + "\n".join(stylesheets)
    font_re = re.compile(r"font-family\s*:\s*([^;}{]+)", re.IGNORECASE)
    fonts = Counter()
    for m in font_re.finditer(all_text):
        family = m.group(1).strip().strip("'\"")
        # Take first font in stack
        first = family.split(",")[0].strip().strip("'\"")
        skip = ("inherit", "initial", "unset", "monospace", "sans-serif", "serif")
        if first.lower() in skip or first.startswith("var(") or first.startswith("-"):
            continue
        fonts[first] += 1
    return [f for f, _ in fonts.most_common()]


def fetch_page(url: str) -> tuple[str, list[str]]:
    """Fetch HTML and linked stylesheets from a URL."""
    headers = {"User-Agent": "Mozilla/5.0 (chart-library theme extractor)"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    html = resp.text
    soup = BeautifulSoup(html, "lxml")

    stylesheets = []
    # Inline <style> tags
    for tag in soup.find_all("style"):
        if tag.string:
            stylesheets.append(tag.string)

    # Linked stylesheets
    for link in soup.find_all("link", rel="stylesheet"):
        href = link.get("href")
        if href:
            if href.startswith("//"):
                href = "https:" + href
            elif href.startswith("/"):
                parsed = urlparse(url)
                href = f"{parsed.scheme}://{parsed.netloc}{href}"
            elif not href.startswith("http"):
                href = url.rstrip("/") + "/" + href
            try:
                css_resp = requests.get(href, headers=headers, timeout=10)
                if css_resp.ok:
                    stylesheets.append(css_resp.text)
            except Exception:
                pass

    return html, stylesheets


# ── Palette building ─────────────────────────────────────────────────────────

def build_palette(colors: list[str]) -> dict:
    """
    From raw extracted colors, build a theme palette.

    Returns dict with keys: background, plot_background, palette (7 colors),
    text_title, text_subtitle, text_axis, text_source, grid, spines,
    table_header_bg, map_land, map_ocean.
    """
    if not colors:
        # Fallback to default-like defaults
        return _default_palette()

    # Separate colors by luminance
    lights = [c for c in colors if _luminance(c) > 0.85]
    darks = [c for c in colors if _luminance(c) < 0.2]
    mids = [c for c in colors if 0.2 <= _luminance(c) <= 0.85]

    # Chromatic colors (saturated and not too light or too dark)
    chromatic = [c for c in colors
                 if _saturation(c) > 0.15
                 and 0.15 < _luminance(c) < 0.85]
    # Deduplicate similar colors (distance < 30)
    unique_chromatic = _dedupe_colors(chromatic, threshold=40)

    # Background: lightest color, or white
    background = lights[0] if lights else "#FFFFFF"
    # Slightly tint the background toward the dominant chromatic color
    if unique_chromatic and background == "#FFFFFF":
        background = "#FAFAFA"

    # Title text: darkest color
    text_title = darks[0] if darks else "#1C2B3A"
    text_subtitle = _lighten(text_title, 0.3)
    text_axis = _lighten(text_title, 0.5)
    text_source = text_axis

    # Data palette: up to 7 chromatic colors, sorted by distance from each other
    palette = _pick_diverse_colors(unique_chromatic, 7)
    if len(palette) < 2:
        palette = ["#1C2B3A", "#4A7C59", "#C4A575", "#2B6C8F", "#7B1A2A", "#A8D5E8", "#D89B9E"]

    # Grid/spine: light version of background
    grid_color = _darken(background, 0.06)
    spine_color = _darken(background, 0.12)

    # Table header: dark chromatic or title color
    table_header = text_title

    # Map colors
    map_land = _darken(background, 0.04)
    map_ocean = _darken(background, 0.08)

    return {
        "background": background,
        "plot_background": background,
        "palette": palette,
        "text_title": text_title,
        "text_subtitle": text_subtitle,
        "text_axis": text_axis,
        "text_source": text_source,
        "grid": grid_color,
        "spines": spine_color,
        "table_header_bg": table_header,
        "map_land": map_land,
        "map_ocean": map_ocean,
    }


def _default_palette():
    return {
        "background": "#F0EBE3",
        "plot_background": "#F0EBE3",
        "palette": ["#7B1A2A", "#2B6C8F", "#4A7C59", "#C4A575", "#1F3B54", "#A8D5E8", "#D89B9E"],
        "text_title": "#1C2B3A",
        "text_subtitle": "#5A6472",
        "text_axis": "#9AA3AC",
        "text_source": "#9AA3AC",
        "grid": "#E0DAD0",
        "spines": "#C8C0B4",
        "table_header_bg": "#1C2B3A",
        "map_land": "#E8E4DC",
        "map_ocean": "#D4D0CA",
    }


def _dedupe_colors(colors: list[str], threshold: float = 40) -> list[str]:
    """Remove colors that are too similar to already-kept ones."""
    kept = []
    for c in colors:
        if all(_color_distance(c, k) > threshold for k in kept):
            kept.append(c)
    return kept


def _pick_diverse_colors(colors: list[str], n: int) -> list[str]:
    """Pick up to n colors that are maximally different from each other."""
    if len(colors) <= n:
        return colors
    picked = [colors[0]]
    remaining = colors[1:]
    while len(picked) < n and remaining:
        # Pick the color most distant from all picked colors
        best = max(remaining, key=lambda c: min(_color_distance(c, p) for p in picked))
        picked.append(best)
        remaining.remove(best)
    return picked


def _lighten(hex_color: str, amount: float) -> str:
    """Lighten a color by blending toward white."""
    r, g, b = _hex_to_rgb(hex_color)
    r = int(r + (255 - r) * amount)
    g = int(g + (255 - g) * amount)
    b = int(b + (255 - b) * amount)
    return _rgb_to_hex(r, g, b)


def _darken(hex_color: str, amount: float) -> str:
    """Darken a color by blending toward black."""
    r, g, b = _hex_to_rgb(hex_color)
    r = int(r * (1 - amount))
    g = int(g * (1 - amount))
    b = int(b * (1 - amount))
    return _rgb_to_hex(r, g, b)


# ── Theme YAML generation ───────────────────────────────────────────────────

def generate_theme_yaml(name: str, pal: dict, font_family: str) -> str:
    """Generate a theme.yaml string."""
    palette_lines = "\n".join(f'  - "{c}"' for c in pal["palette"])

    return f"""name: {name}
version: "1.0"
description: Auto-generated theme from website color extraction

# ── Background ────────────────────────────────────────────────────────────────
background: "{pal['background']}"
plot_background: "{pal['plot_background']}"

# ── Text colors ───────────────────────────────────────────────────────────────
text:
  title: "{pal['text_title']}"
  subtitle: "{pal['text_subtitle']}"
  axis: "{pal['text_axis']}"
  source: "{pal['text_source']}"
  label: "{pal['text_subtitle']}"

# ── Data palette ──────────────────────────────────────────────────────────────
palette:
{palette_lines}

# ── Typography ────────────────────────────────────────────────────────────────
fonts:
  family: '{font_family}'

font_sizes:
  title: 22
  subtitle: 13
  axis_tick: 10
  axis_label: 11
  source: 9
  data_label: 9

font_weights:
  title: "bold"
  subtitle: "normal"

# ── Layout ────────────────────────────────────────────────────────────────────
margins:
  top: 90
  bottom: 60
  left: 60
  right: 50

# ── Grid ──────────────────────────────────────────────────────────────────────
grid:
  color: "{pal['grid']}"
  width: 1
  horizontal: true
  vertical: false

# ── Spines ────────────────────────────────────────────────────────────────────
spines:
  top: false
  right: false
  color: "{pal['spines']}"
  width: 1

# ── Legend ────────────────────────────────────────────────────────────────────
legend:
  position: "bottom"
  orientation: "h"
  marker: "circle"
  border: false

# ── Branding ──────────────────────────────────────────────────────────────────
branding:
  show: true
  text: "{name.upper()}"
  position: "bottom_right"
  color: "{pal['text_title']}"
  font_size: 10
  font_weight: "bold"

# ── Source attribution ────────────────────────────────────────────────────────
source:
  prefix: "Source: "
  position: "bottom_left"
  italic: true

# ── Chart-type overrides ──────────────────────────────────────────────────────
bar:
  gap: 0.25
  group_gap: 0.05

line:
  width: 2.5
  end_labels: true
  markers: false
  marker_size: 6

area:
  opacity: 0.75
  line_width: 0

scatter:
  marker_size: 8
  opacity: 0.8

pie:
  hole: 0.55

table:
  header_background: "{pal['table_header_bg']}"
  header_text: "#FFFFFF"
  highlight_color: "{pal['palette'][3] if len(pal['palette']) > 3 else pal['palette'][0]}"
  border_color: "{pal['grid']}"

map:
  land_color: "{pal['map_land']}"
  ocean_color: "{pal['map_ocean']}"
  border_color: "{pal['spines']}"

stat_card:
  value_font_size: 48
  label_font_size: 14
  border_radius: 12

big_number:
  value_font_size: 56
  label_font_size: 13

gauge:
  arc_bg_color: "{pal['grid']}"
  value_font_size: 32
  label_font_size: 13
  min_max_font_size: 11
"""


# ── Example file generation ──────────────────────────────────────────────────

# Chart types and their function names / import patterns
CHART_TYPES = [
    # (filename_stem, function_name, has_data_from_default, special_scatter)
    ("bar",            "bar",            True,  False),
    ("line",           "line",           True,  False),
    ("area",           "area",           True,  False),
    ("scatter",        "scatter",        True,  True),
    ("pie",            "pie",            True,  False),
    ("table",          "table",          True,  False),
    ("map",            "map_chart",      True,  False),
    ("diverging_bar",  "diverging_bar",  True,  False),
    ("sparkline_line", "sparkline_line", True,  False),
    ("sparkline_area", "sparkline_area", True,  False),
    ("sparkline_bar",  "sparkline_bar",  True,  False),
    ("stat_card",      "stat_card",      False, False),
    ("big_number",     "big_number",     False, False),
    ("gauge",          "gauge",          False, False),
]


def _example_py(stem: str, func_name: str, has_data: bool, is_scatter: bool, theme_name: str) -> str:
    """Generate a single example .py file."""
    # Special cases: map uses map_chart import name
    import_name = func_name
    src_module = stem  # e.g. "bar", "line", etc.
    if stem == "map":
        src_module = "map"

    lines = [f'"""{stem.replace("_", " ").title()} example — {theme_name} theme."""', ""]
    lines += ["import os", "import sys"]
    lines += ['sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))']

    if has_data:
        lines += ['sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../default"))']

    lines += ["", "import json"]

    if has_data:
        lines += [f"import {src_module} as _src"]

    lines += [f"from chart_library import {import_name}, save_png, save_svg"]
    lines += ["", 'OUT = os.path.dirname(__file__)', ""]
    lines += [f"", f'_CFG = os.path.join(os.path.dirname(__file__), "{stem}.json")', ""]
    lines += ["", "def make_fig(cfg_path=_CFG):"]
    lines += ["    with open(cfg_path) as f:", "        cfg = json.load(f)"]

    if has_data:
        # bar example uses _df2 (the stacked dataset)
        data_ref = "_src._df2" if stem == "bar" else "_src._df"
        lines += [f"    fig = {import_name}({data_ref}, **cfg)"]
        if is_scatter:
            lines += ['    fig.update_xaxes(type="log", title_text="Cost per 1M Tokens ($)")']
            lines += ['    fig.update_yaxes(type="log", title_text="Total Usage in Millions of Tokens")']
        lines += ["    return fig"]
    else:
        lines += [f"    return {import_name}(**cfg)"]

    output_stem = "bar_stacked" if stem == "bar" else stem
    lines += ["", ""]
    lines += ['if __name__ == "__main__":']
    lines += ["    fig = make_fig()"]
    lines += [f'    save_png(fig, os.path.join(OUT, "{output_stem}.png"))']
    lines += [f'    save_svg(fig, os.path.join(OUT, "{output_stem}.svg"))']
    lines += [f'    fig.write_html(os.path.join(OUT, "{output_stem}.html"))']
    lines += [f'    print("{output_stem}.png + {output_stem}.svg written")']
    lines += [""]

    return "\n".join(lines)


def create_json_configs(theme_name: str, src_dir: str, dest_dir: str):
    """Copy JSON configs from default, setting the theme name on all."""
    for fname in os.listdir(src_dir):
        if not fname.endswith(".json"):
            continue
        src_path = os.path.join(src_dir, fname)
        dest_path = os.path.join(dest_dir, fname)
        with open(src_path) as f:
            cfg = json.load(f)
        # Always set theme — some configs (stat_card, big_number, gauge) don't have it
        cfg["theme"] = theme_name
        with open(dest_path, "w") as f:
            json.dump(cfg, f, indent=4)
            f.write("\n")


def create_generate_all(theme_name: str, dest_dir: str):
    """Create the generate_all.py for a new theme by adapting care-indeed's."""
    src = os.path.join(REPO_ROOT, "examples", "care-indeed", "generate_all.py")
    with open(src) as f:
        content = f.read()

    # Replace theme references
    content = content.replace("care-indeed", theme_name)
    content = content.replace("Care Indeed", theme_name.replace("-", " ").title())

    # Fix the font-family in the HTML — extract from the theme we're about to create
    # (will be fixed up after theme YAML is written)

    dest = os.path.join(dest_dir, "generate_all.py")
    with open(dest, "w") as f:
        f.write(content)


def update_generate_all_style(theme_name: str, dest_dir: str, pal: dict, font_family: str):
    """Patch the generate_all.py HTML styles to use the new theme's colors/fonts."""
    path = os.path.join(dest_dir, "generate_all.py")
    with open(path) as f:
        content = f.read()

    # The care-indeed generate_all.py has hardcoded colors — replace them
    replacements = {
        # Background
        "#FFFAF7": pal["background"],
        # Title/text
        "#1F1C1B": pal["text_title"],
        "#7A7470": pal["text_axis"],
        "#9E9691": pal["text_source"],
        # Borders
        "#D9D6D5": pal["spines"],
        "#E5E4E3": pal["grid"],
        # Accent (download button, section headers)
        "#FF6B35": pal["palette"][0],
        "#E05520": _darken(pal["palette"][0], 0.12),
        # Code background
        "#F0EDE8": _darken(pal["background"], 0.03),
        "#FAFAF8": _lighten(pal["background"], 0.02),
        # Font family
        "Montserrat, Roboto, sans-serif": font_family,
    }

    for old, new in replacements.items():
        content = content.replace(old, new)

    with open(path, "w") as f:
        f.write(content)


# ── Index page ───────────────────────────────────────────────────────────────

def update_index():
    """Generate examples/index.html linking to all theme galleries."""
    examples_dir = os.path.join(REPO_ROOT, "examples")
    themes = []
    for d in sorted(os.listdir(examples_dir)):
        all_html = os.path.join(examples_dir, d, "all.html")
        if os.path.isfile(all_html):
            themes.append(d)

    rows = "\n".join(
        f'      <li><a href="{t}/all.html">{t}</a></li>'
        for t in themes
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

    path = os.path.join(examples_dir, "index.html")
    with open(path, "w") as f:
        f.write(html)
    print(f"Index written to {path}")
    return themes


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    url = input("Website URL: ").strip()
    if not url.startswith("http"):
        url = "https://" + url

    # Derive theme name from domain
    domain = urlparse(url).netloc.replace("www.", "")
    suggested = domain.split(".")[0]
    theme_name = input(f"Theme name [{suggested}]: ").strip() or suggested
    theme_name = re.sub(r"[^a-z0-9-]", "-", theme_name.lower()).strip("-")

    print(f"\nFetching {url}...")
    html, stylesheets = fetch_page(url)

    print("Extracting colors and fonts...")
    colors = extract_colors(html, stylesheets)
    fonts = extract_fonts(html, stylesheets)

    print(f"  Found {len(colors)} colors, {len(fonts)} font families")
    if colors:
        print(f"  Top colors: {colors[:10]}")
    if fonts:
        print(f"  Top fonts: {fonts[:5]}")

    # Build palette
    pal = build_palette(colors)

    # Font family: use extracted fonts or fall back to system stack
    if fonts:
        # Build a font stack from top 2 extracted fonts + generic fallback
        stack = fonts[:2]
        last = fonts[0].lower()
        if any(kw in last for kw in ("serif",)):
            stack.append("serif")
        else:
            stack.append("sans-serif")
        font_family = ", ".join(f'"{f}"' if " " in f else f for f in stack)
    else:
        font_family = "Georgia, 'Times New Roman', serif"

    print(f"\nTheme: {theme_name}")
    print(f"  Background: {pal['background']}")
    print(f"  Palette: {pal['palette']}")
    print(f"  Font: {font_family}")

    # ── Create theme YAML ────────────────────────────────────────────────────
    theme_yaml = generate_theme_yaml(theme_name, pal, font_family)

    # themes/<name>/theme.yaml
    theme_dir = os.path.join(REPO_ROOT, "themes", theme_name)
    os.makedirs(theme_dir, exist_ok=True)
    yaml_path = os.path.join(theme_dir, "theme.yaml")
    with open(yaml_path, "w") as f:
        f.write(theme_yaml)
    print(f"\n  Wrote {yaml_path}")

    # scripts/chart_library/themes/<name>.yaml (bundled copy)
    bundled_path = os.path.join(REPO_ROOT, "scripts", "chart_library", "themes", f"{theme_name}.yaml")
    with open(bundled_path, "w") as f:
        f.write(theme_yaml)
    print(f"  Wrote {bundled_path}")

    # ── Create examples ──────────────────────────────────────────────────────
    examples_dir = os.path.join(REPO_ROOT, "examples", theme_name)
    os.makedirs(examples_dir, exist_ok=True)

    # Copy JSON configs from default, swapping theme name
    a16z_dir = os.path.join(REPO_ROOT, "examples", "default")
    create_json_configs(theme_name, a16z_dir, examples_dir)
    print(f"  Created JSON configs in {examples_dir}/")

    # Generate example .py files
    for stem, func_name, has_data, is_scatter in CHART_TYPES:
        py_content = _example_py(stem, func_name, has_data, is_scatter, theme_name)
        py_path = os.path.join(examples_dir, f"{stem}.py")
        with open(py_path, "w") as f:
            f.write(py_content)
    print(f"  Created example .py files")

    # Generate generate_all.py
    create_generate_all(theme_name, examples_dir)
    update_generate_all_style(theme_name, examples_dir, pal, font_family)
    print(f"  Created generate_all.py")

    # ── Run examples to generate PNGs/SVGs ───────────────────────────────────
    print("\nGenerating chart images...")
    venv_python = os.path.join(REPO_ROOT, "venv", "bin", "python")
    if not os.path.exists(venv_python):
        venv_python = sys.executable

    for stem, _, _, _ in CHART_TYPES:
        py_path = os.path.join(examples_dir, f"{stem}.py")
        result = subprocess.run(
            [venv_python, py_path],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            print(f"  WARNING: {stem}.py failed: {result.stderr[:200]}")
        else:
            print(f"  {result.stdout.strip()}")

    # ── Generate all.html gallery ────────────────────────────────────────────
    print("\nBuilding gallery...")
    gen_path = os.path.join(examples_dir, "generate_all.py")
    result = subprocess.run(
        [venv_python, gen_path],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        print(f"  WARNING: generate_all.py failed: {result.stderr[:300]}")
    else:
        print(f"  {result.stdout.strip()}")

    # ── Update index page ────────────────────────────────────────────────────
    themes = update_index()

    # ── Print preview links ──────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("DONE! Preview links:")
    print(f"  Local:  file://{os.path.join(examples_dir, 'all.html')}")
    print(f"  After push:")
    for t in themes:
        print(f"    https://raw.githack.com/marksher/a16z-chart-library/main/examples/{t}/all.html")
    print(f"\n  Index:  https://raw.githack.com/marksher/a16z-chart-library/main/examples/index.html")
    print("=" * 60)


if __name__ == "__main__":
    main()
