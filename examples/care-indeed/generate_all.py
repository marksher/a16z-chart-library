"""
Generate all.html — a gallery of all 7 chart types using the care-indeed theme.
Each section shows: chart type / interactive / PNG / SVG side by side.
Run from the repo root: python examples/care-indeed/generate_all.py
"""

import os
import sys
import base64
import importlib.util

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

EXAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))

# Add a16z-news to sys.path so care-indeed modules can resolve their data imports.
# Do NOT add care-indeed itself — that causes circular name collisions since
# both directories share the same filenames (bar.py, line.py, …).
sys.path.insert(0, os.path.join(EXAMPLES_DIR, "../a16z-news"))

from chart_library import load_theme


def _load(name: str):
    """Load a care-indeed example module by file path, avoiding sys.modules collisions."""
    path = os.path.join(EXAMPLES_DIR, f"{name}.py")
    spec = importlib.util.spec_from_file_location(f"ci_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bar_ex     = _load("bar")
line_ex    = _load("line")
area_ex    = _load("area")
scatter_ex = _load("scatter")
pie_ex     = _load("pie")
table_ex   = _load("table")
map_ex     = _load("map")

# ── Chart registry: (display name, figure, png filename, svg filename) ────────
CHARTS = [
    ("Bar",     bar_ex.make_fig(),     "bar_stacked.png", "bar_stacked.svg"),
    ("Line",    line_ex.make_fig(),    "line.png",        "line.svg"),
    ("Area",    area_ex.make_fig(),    "area.png",        "area.svg"),
    ("Scatter", scatter_ex.make_fig(), "scatter.png",     "scatter.svg"),
    ("Pie",     pie_ex.make_fig(),     "pie.png",         "pie.svg"),
    ("Table",   table_ex.make_fig(),   "table.png",       "table.svg"),
    ("Map",     map_ex.make_fig(),     "map.png",         "map.svg"),
]


def encode_file(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# ── Theme swatch ──────────────────────────────────────────────────────────────
t = load_theme("care-indeed")


def _swatch_item(color: str, name: str = "") -> str:
    label = f'<span class="swatch-name">{name}</span>' if name else ""
    return (
        f'<div class="swatch-item">'
        f'<div class="swatch-box" style="background:{color}"></div>'
        f'<span class="swatch-hex">{color}</span>{label}'
        f'</div>'
    )


palette_html = "".join(_swatch_item(c) for c in t.palette)
ui_html = "".join(_swatch_item(c, n) for c, n in [
    (t.background,       "background"),
    (t.text["title"],    "title"),
    (t.text["subtitle"], "subtitle"),
    (t.text["axis"],     "axis"),
    (t.text["source"],   "source"),
    (t.grid["color"],    "grid"),
    (t.spines["color"],  "spines"),
])

swatch_section = f"""
  <section class="swatch-section">
    <h2>Theme Colors</h2>
    <div class="swatch-group">
      <div class="swatch-group-label">Data Palette</div>
      <div class="swatch-row">{palette_html}</div>
    </div>
    <div class="swatch-group">
      <div class="swatch-group-label">UI Colors</div>
      <div class="swatch-row">{ui_html}</div>
    </div>
  </section>
"""

# ── Build chart sections ──────────────────────────────────────────────────────
sections = []
for i, (name, fig, png_name, svg_name) in enumerate(CHARTS):
    png_path = os.path.join(EXAMPLES_DIR, png_name)
    svg_path = os.path.join(EXAMPLES_DIR, svg_name)
    png_b64 = encode_file(png_path)
    svg_b64 = encode_file(svg_path)

    fig.update_layout(autosize=True)
    include_plotlyjs = "cdn" if i == 0 else False
    chart_html = fig.to_html(include_plotlyjs=include_plotlyjs, full_html=False,
                              config={"displayModeBar": False, "responsive": True})

    section = f"""
  <section class="chart-section">
    <h2>{name}</h2>
    <div class="chart-row">
      <div class="chart-pane chart-interactive">
        <div class="pane-label">Interactive</div>
        {chart_html}
      </div>
      <div class="chart-pane chart-static">
        <div class="pane-label">PNG export</div>
        <img src="data:image/png;base64,{png_b64}" alt="{name} chart PNG" />
      </div>
      <div class="chart-pane chart-svg">
        <div class="pane-label">SVG export</div>
        <img src="data:image/svg+xml;base64,{svg_b64}" alt="{name} chart SVG" />
      </div>
    </div>
  </section>"""
    sections.append(section)

html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Chart Library — Care Indeed Theme</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: Montserrat, Roboto, sans-serif;
      background: #FFFAF7;
      color: #1F1C1B;
      padding: 40px 32px 80px;
    }

    header {
      margin-bottom: 40px;
      border-bottom: 2px solid #D9D6D5;
      padding-bottom: 24px;
    }

    header h1 {
      font-size: 28px;
      font-weight: bold;
      color: #1F1C1B;
      margin-bottom: 6px;
    }

    header p {
      font-size: 13px;
      color: #7A7470;
      font-style: italic;
    }

    /* ── Swatch ── */
    .swatch-section {
      margin-bottom: 56px;
      padding: 24px;
      background: #FFFAF7;
      border: 1px solid #D9D6D5;
      border-radius: 4px;
    }

    .swatch-section h2 {
      font-size: 14px;
      font-weight: bold;
      color: #1F1C1B;
      margin-bottom: 20px;
      text-transform: uppercase;
      letter-spacing: 0.07em;
    }

    .swatch-group { margin-bottom: 16px; }
    .swatch-group:last-child { margin-bottom: 0; }

    .swatch-group-label {
      font-size: 10px;
      font-weight: bold;
      color: #9E9691;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 10px;
    }

    .swatch-row { display: flex; flex-wrap: wrap; gap: 12px; }

    .swatch-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 4px;
    }

    .swatch-box {
      width: 44px;
      height: 44px;
      border-radius: 4px;
      border: 1px solid rgba(0,0,0,0.08);
    }

    .swatch-hex {
      font-size: 9px;
      color: #7A7470;
      font-family: monospace;
    }

    .swatch-name {
      font-size: 9px;
      color: #9E9691;
    }

    /* ── Chart sections ── */
    .chart-section { margin-bottom: 72px; }

    .chart-section h2 {
      font-size: 20px;
      font-weight: bold;
      color: #FF6B35;
      margin-bottom: 16px;
      padding-bottom: 8px;
      border-bottom: 1px solid #E5E4E3;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .chart-row {
      display: flex;
      gap: 20px;
      align-items: flex-start;
    }

    .chart-pane {
      flex: 1;
      background: #FFFAF7;
      border: 1.5px solid #D9D6D5;
      border-radius: 4px;
      padding: 16px;
      min-width: 0;
    }

    .pane-label {
      font-size: 10px;
      font-weight: bold;
      color: #9E9691;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 12px;
    }

    .chart-pane img {
      width: 100%;
      height: auto;
      display: block;
    }

    .chart-interactive .plotly-graph-div {
      width: 100% !important;
    }

    @media (max-width: 1100px) {
      .chart-row { flex-direction: column; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Chart Library</h1>
    <p>All chart types — interactive Plotly / PNG export / SVG export. Theme: care-indeed.</p>
  </header>
""" + swatch_section + "\n".join(sections) + """
</body>
</html>
"""

out_path = os.path.join(EXAMPLES_DIR, "all.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"all.html written to {out_path}")
