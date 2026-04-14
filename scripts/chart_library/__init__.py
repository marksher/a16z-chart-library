"""
chart_library — Themeable Plotly chart library.

All chart functions return a ``plotly.graph_objects.Figure``.  Display it
interactively with ``fig.show()`` or export as PNG with ``save_png(fig, "out.png")``.

Quick start
-----------
>>> import pandas as pd
>>> from chart_library import bar, save_png
>>>
>>> df = pd.DataFrame({"company": ["OpenAI", "Anthropic", "Google"],
...                    "revenue": [3.7, 0.8, 2.1]})
>>> fig = bar(df, x="company", y="revenue",
...           title="AI Revenue (2025)",
...           subtitle="Billions USD",
...           source="Company filings")
>>> fig.show()                    # interactive
>>> save_png(fig, "revenue.png")  # static PNG

Swap themes
-----------
>>> fig = bar(df, x="company", y="revenue", theme="path/to/mytheme.yaml")
>>> fig = bar(df, x="company", y="revenue", theme=None)  # Plotly defaults
"""

from .charts.bar import bar
from .charts.diverging_bar import diverging_bar
from .charts.line import line
from .charts.area import area
from .charts.scatter import scatter
from .charts.sparkline import sparkline, sparkline_line, sparkline_area, sparkline_bar
from .charts.pie import pie
from .charts.table import table
from .charts.map import map_chart
from .charts.stat_card import stat_card
from .charts.big_number import big_number
from .themes.base import load_theme, Theme
from .utils.layout import save_png, save_svg

__version__ = "0.1.0"

__all__ = [
    "bar",
    "diverging_bar",
    "line",
    "sparkline",
    "sparkline_line",
    "sparkline_area",
    "sparkline_bar",
    "area",
    "scatter",
    "pie",
    "table",
    "map_chart",
    "stat_card",
    "big_number",
    "load_theme",
    "Theme",
    "save_png",
    "save_svg",
]
