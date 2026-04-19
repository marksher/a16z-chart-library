"""
Generate all.html — gallery of all chart types using the quitemailingyourself theme.
Each section shows: chart type / interactive / PNG / SVG at matching sizes,
plus a collapsible Python code snippet.
Run from the repo root: python examples/quitemailingyourself/generate_all.py
"""

import os
import sys
import base64
import re
import html as _html
import importlib.util

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

EXAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))

# Add default to sys.path so quitemailingyourself modules can resolve their data imports.
# Do NOT add quitemailingyourself itself — both dirs share the same filenames.
sys.path.insert(0, os.path.join(EXAMPLES_DIR, "../default"))

from chart_library import load_theme


def _load(name: str):
    """Load a quitemailingyourself example module by file path, avoiding sys.modules collisions."""
    path = os.path.join(EXAMPLES_DIR, f"{name}.py")
    spec = importlib.util.spec_from_file_location(f"ci_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bar_ex           = _load("bar")
line_ex          = _load("line")
area_ex          = _load("area")
scatter_ex       = _load("scatter")
pie_ex           = _load("pie")
table_ex         = _load("table")
map_ex           = _load("map")
diverging_bar_ex = _load("diverging_bar")
sparkline_line_ex = _load("sparkline_line")
sparkline_area_ex = _load("sparkline_area")
sparkline_bar_ex  = _load("sparkline_bar")
stat_card_ex      = _load("stat_card")
big_number_ex     = _load("big_number")
gauge_ex          = _load("gauge")

# ── Chart registry: (display name, figure, png, svg, source file) ─────────────
CHARTS = [
    ("Bar",           bar_ex.make_fig(),            "bar_stacked.png",    "bar_stacked.svg",    "bar.py"),
    ("Line",          line_ex.make_fig(),            "line.png",           "line.svg",           "line.py"),
    ("Area",          area_ex.make_fig(),            "area.png",           "area.svg",           "area.py"),
    ("Scatter",       scatter_ex.make_fig(),         "scatter.png",        "scatter.svg",        "scatter.py"),
    ("Pie",           pie_ex.make_fig(),             "pie.png",            "pie.svg",            "pie.py"),
    ("Table",         table_ex.make_fig(),           "table.png",          "table.svg",          "table.py"),
    ("Map",           map_ex.make_fig(),             "map.png",            "map.svg",            "map.py"),
    ("Diverging Bar", diverging_bar_ex.make_fig(),   "diverging_bar.png",  "diverging_bar.svg",  "diverging_bar.py"),
    ("Sparkline Line",sparkline_line_ex.make_fig(),  "sparkline_line.png", "sparkline_line.svg", "sparkline_line.py"),
    ("Sparkline Area",sparkline_area_ex.make_fig(),  "sparkline_area.png", "sparkline_area.svg", "sparkline_area.py"),
    ("Sparkline Bar", sparkline_bar_ex.make_fig(),   "sparkline_bar.png",  "sparkline_bar.svg",  "sparkline_bar.py"),
    ("Stat Card",    stat_card_ex.make_fig(),       "stat_card.png",      "stat_card.svg",      "stat_card.py"),
    ("Big Number",   big_number_ex.make_fig(),       "big_number.png",     "big_number.svg",     "big_number.py"),
    ("Gauge",        gauge_ex.make_fig(),            "gauge.png",          "gauge.svg",          "gauge.py"),
]


def encode_file(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _extract_snippet(py_path: str) -> str:
    """Read example source, strip run-boilerplate, append export pattern, HTML-escape."""
    with open(py_path, encoding="utf-8") as f:
        src = f.read()

    lines = src.splitlines()
    clean = [ln for ln in lines
             if not ln.strip().startswith("sys.path.insert")
             and ln.strip() != "import sys"]
    src = "\n".join(clean)

    src = re.sub(r'\n\nif __name__ == ["\']__main__["\']:.*$', '', src, flags=re.DOTALL)
    src = re.sub(r'\n{3,}', '\n\n', src)

    src = src.strip()

    # Append standard export pattern
    src += (
        "\n\n\n# ── Export ──────────────────────────────────────────────\n"
        "fig = make_fig()\n"
        'save_png(fig, "chart.png")    # raster PNG  — requires kaleido\n'
        'save_svg(fig, "chart.svg")    # vector SVG  — requires kaleido\n'
        'fig.write_html("chart.html")  # interactive HTML — no extra deps\n'
        "\n"
        "# Embed PNG in HTML (base64)\n"
        "import base64\n"
        'data = base64.b64encode(open("chart.png", "rb").read()).decode()\n'
        'img_tag = f\'<img src="data:image/png;base64,{data}" />\'\n'
    )

    return _html.escape(src)


# ── Theme swatch ──────────────────────────────────────────────────────────────
t = load_theme("quitemailingyourself")


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
for i, (name, fig, png_name, svg_name, py_name) in enumerate(CHARTS):
    png_path  = os.path.join(EXAMPLES_DIR, png_name)
    svg_path  = os.path.join(EXAMPLES_DIR, svg_name)
    py_path   = os.path.join(EXAMPLES_DIR, py_name)
    json_path = os.path.join(EXAMPLES_DIR, py_name.replace(".py", ".json"))

    png_b64   = encode_file(png_path)
    svg_b64   = encode_file(svg_path)
    snippet   = _extract_snippet(py_path)

    with open(json_path, encoding="utf-8") as f:
        json_snippet = _html.escape(f.read().strip())

    chart_w = fig.layout.width or 900
    pane_w  = chart_w + 32

    include_plotlyjs = "cdn" if i == 0 else False
    chart_html = fig.to_html(include_plotlyjs=include_plotlyjs, full_html=False,
                              config={"displayModeBar": False, "responsive": True})

    section = f"""
  <section class="chart-section">
    <h2>{name}</h2>
    <div class="chart-row">
      <div class="chart-pane chart-interactive" style="width:{pane_w}px">
        <div class="pane-label">Interactive</div>
        {chart_html}
      </div>
      <div class="chart-pane chart-static" style="width:{pane_w}px">
        <div class="pane-label">PNG export</div>
        <img src="data:image/png;base64,{png_b64}" alt="{name} chart PNG" />
      </div>
      <div class="chart-pane chart-svg" style="width:{pane_w}px">
        <div class="pane-label">SVG export</div>
        <img src="data:image/svg+xml;base64,{svg_b64}" alt="{name} chart SVG" />
      </div>
    </div>
    <details class="code-snippet">
      <summary>JSON config</summary>
      <pre><code class="language-json">{json_snippet}</code></pre>
    </details>
    <details class="code-snippet">
      <summary>Python</summary>
      <pre><code class="language-python">{snippet}</code></pre>
    </details>
  </section>"""
    sections.append(section)

html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Chart Library — Quitemailingyourself Theme</title>
  <link rel="stylesheet"
        href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css" />
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: "IBM Plex Mono", "IBM Plex Sans", sans-serif;
      background: #FAFAFA;
      color: #111111;
      padding: 40px 32px 80px;
    }

    header {
      margin-bottom: 40px;
      border-bottom: 2px solid #DCDCDC;
      padding-bottom: 24px;
    }

    .header-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }
    header h1 { font-size: 28px; font-weight: bold; color: #111111; margin-bottom: 6px; }
    header p  { font-size: 13px; color: #888888; font-style: italic; }

    .dl-btn {
      flex-shrink: 0;
      padding: 8px 16px;
      background: #7C3AED;
      color: #FAFAFA;
      font-family: "IBM Plex Mono", "IBM Plex Sans", sans-serif;
      font-size: 12px;
      font-weight: bold;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      letter-spacing: 0.04em;
      white-space: nowrap;
    }
    .dl-btn:hover { background: #6D33D0; }

    /* ── Swatch ── */
    .swatch-section {
      margin-bottom: 56px; padding: 24px;
      background: #FAFAFA;
      border: 1px solid #DCDCDC; border-radius: 4px;
    }

    .swatch-section h2 {
      font-size: 14px; font-weight: bold; color: #111111;
      margin-bottom: 20px; text-transform: uppercase; letter-spacing: 0.07em;
    }

    .swatch-group { margin-bottom: 16px; }
    .swatch-group:last-child { margin-bottom: 0; }

    .swatch-group-label {
      font-size: 10px; font-weight: bold; color: #888888;
      text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 10px;
    }

    .swatch-row { display: flex; flex-wrap: wrap; gap: 12px; }
    .swatch-item { display: flex; flex-direction: column; align-items: center; gap: 4px; }

    .swatch-box { width: 44px; height: 44px; border-radius: 4px; border: 1px solid rgba(0,0,0,0.08); }
    .swatch-hex { font-size: 9px; color: #888888; font-family: monospace; }
    .swatch-name { font-size: 9px; color: #888888; }

    /* ── Chart sections ── */
    .chart-section { margin-bottom: 72px; }

    .chart-section h2 {
      font-size: 20px; font-weight: bold; color: #7C3AED;
      margin-bottom: 16px; padding-bottom: 8px;
      border-bottom: 1px solid #EBEBEB;
      text-transform: uppercase; letter-spacing: 0.05em;
    }

    .chart-row {
      display: flex; gap: 20px;
      overflow-x: auto; flex-wrap: nowrap;
      padding-bottom: 8px;
    }

    .chart-pane {
      flex-shrink: 0;
      background: #FAFAFA;
      border: 1.5px solid #DCDCDC;
      border-radius: 4px;
      padding: 16px;
    }

    .pane-label {
      font-size: 10px; font-weight: bold; color: #888888;
      text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px;
    }

    .chart-pane img { width: 100%; height: auto; display: block; }
    .chart-interactive .plotly-graph-div { width: 100% !important; }

    /* ── Code snippet ── */
    .code-snippet {
      margin-top: 12px;
      border: 1px solid #DCDCDC;
      border-radius: 4px;
      overflow: hidden;
    }

    .code-snippet summary {
      padding: 8px 14px;
      cursor: pointer;
      font-family: "IBM Plex Mono", "IBM Plex Sans", sans-serif;
      font-size: 11px;
      font-weight: bold;
      color: #888888;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      background: #F2F2F2;
      user-select: none;
      list-style: none;
    }

    .code-snippet summary::-webkit-details-marker { display: none; }
    .code-snippet summary::before { content: "▶ "; font-size: 9px; }
    details[open].code-snippet summary::before { content: "▼ "; }

    .code-snippet pre { margin: 0; overflow-x: auto; background: #FAFAFA; }

    .code-snippet code.hljs {
      font-size: 12px; line-height: 1.55;
      background: #FAFAFA; padding: 16px 20px;
    }
  </style>
</head>
<body>
  <header>
    <div class="header-row">
      <div>
        <h1>Chart Library</h1>
        <p>All chart types — interactive Plotly / PNG export / SVG export. Theme: quitemailingyourself.</p>
      </div>
      <button class="dl-btn" onclick="dlPage('chart-library-quitemailingyourself.html')">&#8595; Download HTML</button>
    </div>
  </header>
""" + swatch_section + "\n".join(sections) + """
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
  <script>
    document.querySelectorAll('.code-snippet').forEach(el => {
      el.addEventListener('toggle', () => {
        if (el.open) hljs.highlightAll();
      });
    });

    function dlPage(fname) {
      var html = '<!DOCTYPE html>' + document.documentElement.outerHTML;
      var blob = new Blob([html], {type: 'text/html'});
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = fname;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(a.href);
    }
  </script>
</body>
</html>
"""

out_path = os.path.join(EXAMPLES_DIR, "all.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"all.html written to {out_path}")
