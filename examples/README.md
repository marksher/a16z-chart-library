# Chart Library — Examples

Interactive galleries of every chart type, rendered in each theme.
Each gallery is a single self-contained HTML file (all images embedded as base64).

---

## Galleries

| Theme | Preview | Download |
|-------|---------|----------|
| **a16z-news** | [Open preview](https://htmlpreview.github.io/?https://github.com/marksher/a16z-chart-library/blob/main/examples/a16z-news/all.html) | [Download HTML](https://raw.githubusercontent.com/marksher/a16z-chart-library/main/examples/a16z-news/all.html) |
| **care-indeed** | [Open preview](https://htmlpreview.github.io/?https://github.com/marksher/a16z-chart-library/blob/main/examples/care-indeed/all.html) | [Download HTML](https://raw.githubusercontent.com/marksher/a16z-chart-library/main/examples/care-indeed/all.html) |

Each gallery also has a **↓ Download HTML** button in the top-right corner that saves
the current page (including all embedded images) as a standalone file.

---

## Chart Types

| Chart | a16z-news source | care-indeed source |
|-------|-----------------|-------------------|
| Bar (stacked) | [bar.py](a16z-news/bar.py) | [bar.py](care-indeed/bar.py) |
| Line | [line.py](a16z-news/line.py) | [line.py](care-indeed/line.py) |
| Area | [area.py](a16z-news/area.py) | [area.py](care-indeed/area.py) |
| Scatter | [scatter.py](a16z-news/scatter.py) | [scatter.py](care-indeed/scatter.py) |
| Pie | [pie.py](a16z-news/pie.py) | [pie.py](care-indeed/pie.py) |
| Table | [table.py](a16z-news/table.py) | [table.py](care-indeed/table.py) |
| Map | [map.py](a16z-news/map.py) | [map.py](care-indeed/map.py) |
| Diverging Bar | [diverging_bar.py](a16z-news/diverging_bar.py) | [diverging_bar.py](care-indeed/diverging_bar.py) |
| Sparkline Line | [sparkline_line.py](a16z-news/sparkline_line.py) | [sparkline_line.py](care-indeed/sparkline_line.py) |
| Sparkline Area | [sparkline_area.py](a16z-news/sparkline_area.py) | [sparkline_area.py](care-indeed/sparkline_area.py) |
| Sparkline Bar | [sparkline_bar.py](a16z-news/sparkline_bar.py) | [sparkline_bar.py](care-indeed/sparkline_bar.py) |

---

## Saving charts

Every example exports three formats from the same `make_fig()` call:

```python
from chart_library import bar, save_png, save_svg

fig = bar(df, x="year", y=["A", "B"], theme="a16z-news", width=900, height=560)

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

## Regenerating galleries

From the repo root:

```bash
python examples/generate_all.py           # a16z-news → examples/a16z-news/all.html
python examples/care-indeed/generate_all.py  # care-indeed → examples/care-indeed/all.html
```
