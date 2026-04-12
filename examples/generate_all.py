"""
Generate all.html — a gallery of all 7 chart types using the a16z-news theme.
Each section shows: <chart type name> / interactive Plotly chart / PNG side by side.
Run from the repo root: python examples/generate_all.py
"""

import os
import sys
import base64

# Add scripts/ to path so chart_library is importable from example files
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

# Add examples/a16z-news/ to path so we can import make_fig from each example
EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "a16z-news")
sys.path.insert(0, EXAMPLES_DIR)

import bar as bar_ex
import line as line_ex
import area as area_ex
import scatter as scatter_ex
import pie as pie_ex
import table as table_ex
import map as map_ex

# ── Chart registry: (display name, figure, png filename) ─────────────────────

CHARTS = [
    ("Bar",     bar_ex.make_fig(),     "bar_stacked.png"),
    ("Line",    line_ex.make_fig(),    "line.png"),
    ("Area",    area_ex.make_fig(),    "area.png"),
    ("Scatter", scatter_ex.make_fig(), "scatter.png"),
    ("Pie",     pie_ex.make_fig(),     "pie.png"),
    ("Table",   table_ex.make_fig(),   "table.png"),
    ("Map",     map_ex.make_fig(),     "map.png"),
]


def encode_png(png_path: str) -> str:
    with open(png_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# ── Build HTML sections ───────────────────────────────────────────────────────

sections = []
for i, (name, fig, png_name) in enumerate(CHARTS):
    png_path = os.path.join(EXAMPLES_DIR, png_name)
    b64 = encode_png(png_path)

    # Make charts responsive so they fill their pane instead of overflowing
    fig.update_layout(autosize=True)

    # First chart includes plotlyjs, rest use existing global
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
        <img src="data:image/png;base64,{b64}" alt="{name} chart PNG" />
      </div>
    </div>
  </section>"""
    sections.append(section)

html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Chart Library — All Chart Types</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: Georgia, 'Times New Roman', serif;
      background: #F0EBE3;
      color: #1C2B3A;
      padding: 40px 32px 80px;
    }

    header {
      margin-bottom: 56px;
      border-bottom: 2px solid #C8C0B4;
      padding-bottom: 24px;
    }

    header h1 {
      font-size: 28px;
      font-weight: bold;
      color: #1C2B3A;
      margin-bottom: 6px;
    }

    header p {
      font-size: 13px;
      color: #5A6472;
      font-style: italic;
    }

    .chart-section {
      margin-bottom: 72px;
    }

    .chart-section h2 {
      font-size: 20px;
      font-weight: bold;
      color: #1C2B3A;
      margin-bottom: 16px;
      padding-bottom: 8px;
      border-bottom: 1px solid #E0DAD0;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .chart-row {
      display: flex;
      gap: 24px;
      align-items: flex-start;
    }

    .chart-pane {
      flex: 1;
      background: #FAF7F4;
      border: 1px solid #E0DAD0;
      border-radius: 4px;
      padding: 16px;
      min-width: 0;
    }

    .pane-label {
      font-size: 10px;
      font-weight: bold;
      color: #9AA3AC;
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

    @media (max-width: 900px) {
      .chart-row { flex-direction: column; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Chart Library</h1>
    <p>All chart types — interactive Plotly (left) vs. PNG export (right). Theme: a16z-news.</p>
  </header>
""" + "\n".join(sections) + """
</body>
</html>
"""

out_path = os.path.join(EXAMPLES_DIR, "all.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"all.html written to {out_path}")
