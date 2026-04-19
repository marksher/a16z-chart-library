# Chart Library — Examples

Interactive galleries of every chart type, rendered in each theme.
Each gallery is a single self-contained HTML file (all images embedded as base64).

---

## Galleries

| Theme | Preview | Download |
|-------|---------|----------|
| **default** | [Open preview](https://raw.githack.com/marksher/a16z-chart-library/main/examples/default/all.html) | [Download HTML](https://raw.githubusercontent.com/marksher/a16z-chart-library/main/examples/default/all.html) |
| **care-indeed** | [Open preview](https://raw.githack.com/marksher/a16z-chart-library/main/examples/care-indeed/all.html) | [Download HTML](https://raw.githubusercontent.com/marksher/a16z-chart-library/main/examples/care-indeed/all.html) |
| **default** | [Open preview](https://raw.githack.com/marksher/a16z-chart-library/main/examples/default/all.html) | [Download HTML](https://raw.githubusercontent.com/marksher/a16z-chart-library/main/examples/default/all.html) |
| **quitemailingyourself** | [Open preview](https://raw.githack.com/marksher/a16z-chart-library/main/examples/quitemailingyourself/all.html) | [Download HTML](https://raw.githubusercontent.com/marksher/a16z-chart-library/main/examples/quitemailingyourself/all.html) |

Each gallery also has a **↓ Download HTML** button in the top-right corner that saves
the current page (including all embedded images) as a standalone file.

---

## Chart Types

| Chart | default | care-indeed | default | quitemailingyourself |
|------------------|-------------|---------|----------------------|
| Bar (stacked) | [bar.py](default/bar.py) | [bar.py](care-indeed/bar.py) | [bar.py](default/bar.py) | [bar.py](quitemailingyourself/bar.py) |
| Line | [line.py](default/line.py) | [line.py](care-indeed/line.py) | [line.py](default/line.py) | [line.py](quitemailingyourself/line.py) |
| Area | [area.py](default/area.py) | [area.py](care-indeed/area.py) | [area.py](default/area.py) | [area.py](quitemailingyourself/area.py) |
| Scatter | [scatter.py](default/scatter.py) | [scatter.py](care-indeed/scatter.py) | [scatter.py](default/scatter.py) | [scatter.py](quitemailingyourself/scatter.py) |
| Pie | [pie.py](default/pie.py) | [pie.py](care-indeed/pie.py) | [pie.py](default/pie.py) | [pie.py](quitemailingyourself/pie.py) |
| Table | [table.py](default/table.py) | [table.py](care-indeed/table.py) | [table.py](default/table.py) | [table.py](quitemailingyourself/table.py) |
| Map | [map.py](default/map.py) | [map.py](care-indeed/map.py) | [map.py](default/map.py) | [map.py](quitemailingyourself/map.py) |
| Diverging Bar | [diverging_bar.py](default/diverging_bar.py) | [diverging_bar.py](care-indeed/diverging_bar.py) | [diverging_bar.py](default/diverging_bar.py) | [diverging_bar.py](quitemailingyourself/diverging_bar.py) |
| Sparkline Line | [sparkline_line.py](default/sparkline_line.py) | [sparkline_line.py](care-indeed/sparkline_line.py) | [sparkline_line.py](default/sparkline_line.py) | [sparkline_line.py](quitemailingyourself/sparkline_line.py) |
| Sparkline Area | [sparkline_area.py](default/sparkline_area.py) | [sparkline_area.py](care-indeed/sparkline_area.py) | [sparkline_area.py](default/sparkline_area.py) | [sparkline_area.py](quitemailingyourself/sparkline_area.py) |
| Sparkline Bar | [sparkline_bar.py](default/sparkline_bar.py) | [sparkline_bar.py](care-indeed/sparkline_bar.py) | [sparkline_bar.py](default/sparkline_bar.py) | [sparkline_bar.py](quitemailingyourself/sparkline_bar.py) |
| Stat Card | [stat_card.py](default/stat_card.py) | [stat_card.py](care-indeed/stat_card.py) | [stat_card.py](default/stat_card.py) | [stat_card.py](quitemailingyourself/stat_card.py) |
| Big Number | [big_number.py](default/big_number.py) | [big_number.py](care-indeed/big_number.py) | [big_number.py](default/big_number.py) | [big_number.py](quitemailingyourself/big_number.py) |
| Gauge | [gauge.py](default/gauge.py) | [gauge.py](care-indeed/gauge.py) | [gauge.py](default/gauge.py) | [gauge.py](quitemailingyourself/gauge.py) |

---

## Saving charts

Every example exports three formats from the same `make_fig()` call:

```python
from chart_library import bar, save_png, save_svg

fig = bar(df, x="year", y=["A", "B"], theme="default", width=900, height=560)

save_png(fig, "chart.png")    # raster PNG  — requires kaleido
save_svg(fig, "chart.svg")    # vector SVG  — requires kaleido
fig.write_html("chart.html")  # interactive HTML — no extra deps
```

Install kaleido for PNG/SVG export:

```bash
pip install kaleido
```

---

## Embedding in HTML

**PNG or SVG via base64** — embed directly in any HTML file, no separate file needed:

```python
import base64

# PNG
with open("chart.png", "rb") as f:
    data = base64.b64encode(f.read()).decode()
img_tag = f'<img src="data:image/png;base64,{data}" />'

# SVG (also works inline as raw <svg> markup)
with open("chart.svg", "rb") as f:
    data = base64.b64encode(f.read()).decode()
img_tag = f'<img src="data:image/svg+xml;base64,{data}" />'
```

**Interactive Plotly** — embed the chart div in an existing page:

```python
chart_html = fig.to_html(
    include_plotlyjs="cdn",   # first chart on page — loads Plotly from CDN
    # include_plotlyjs=False, # subsequent charts — reuse the already-loaded Plotly
    full_html=False,          # returns just the <div>, not a full page
    config={"displayModeBar": False},
)
```

Paste the returned string into your HTML `<body>`. Add one `<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>` tag in `<head>` if using `include_plotlyjs=False`.

---

## JSON config per chart

Each example has a companion `.json` file containing all chart display parameters.
`make_fig()` loads it at call time — the Python file only holds the data definition.

```json
{
  "x": "year",
  "y": ["Microsoft", "Meta", "Alphabet", "Amazon", "Oracle"],
  "title": "Hyperscaler Capex To The Moon",
  "subtitle": "Combined capital expenditures expected to top $650 billion in 2026",
  "source": "Bloomberg",
  "stacked": true,
  "theme": "default",
  "width": 900,
  "height": 560
}
```

Point `make_fig()` at any config file:

```python
fig = bar.make_fig()                        # uses bar.json next to the file
fig = bar.make_fig("my_custom_bar.json")    # point at any other config
```

### Adding a data source (dashboard pattern)

For a dashboard, add a `"data"` block to the JSON. The chart library's
rendering stays the same — a separate loader resolves the data source to a
DataFrame before calling the chart function.

```json
{
  "data": {
    "connection": "postgres_prod",
    "query": "SELECT month, revenue, forecast FROM monthly_revenue WHERE year = 2025"
  },
  "x": "month",
  "y": ["revenue", "forecast"],
  "title": "Monthly Revenue",
  "theme": "default",
  "width": 900,
  "height": 560
}
```

```python
import json
import sqlalchemy as sa

CONNECTIONS = {
    "postgres_prod": "postgresql://user:pass@host/db",  # keep out of the JSON
}

def make_fig(cfg_path):
    cfg = json.load(open(cfg_path))
    data_cfg = cfg.pop("data", None)
    if data_cfg:
        engine = sa.create_engine(CONNECTIONS[data_cfg["connection"]])
        import pandas as pd
        df = pd.read_sql(data_cfg["query"], engine)
    return line(df, **cfg)
```

**Things that get complicated at dashboard scale:**

- **Credentials** — never in the JSON; use named connections resolved from env vars or a secrets manager
- **Filter params** — static queries don't support user filters; add Jinja2 templating (`WHERE year = {{ year }}`) and a params block
- **Caching** — cache query results by (query hash + params), invalidate on TTL or on demand

At the point where you need live filters, multi-user access, and query caching,
look at [Evidence.dev](https://evidence.dev) (SQL + Markdown → static dashboard),
[Streamlit](https://streamlit.io), or [Apache Superset](https://superset.apache.org)
before building that infrastructure yourself.

---

## Regenerating galleries

From the repo root:

```bash
python examples/generate_all.py                        # default
python examples/care-indeed/generate_all.py            # care-indeed
python examples/quitemailingyourself/generate_all.py   # quitemailingyourself
python examples/default/generate_all.py                # default (Plotly defaults)
```

### Create a new theme from any website

```bash
python scripts/create_theme.py
```
