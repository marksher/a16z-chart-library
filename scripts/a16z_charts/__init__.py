"""
a16z_charts — a publication-quality chart package matching the a16z.news visual style.

Quick start:
    import a16z_charts as a16z

    a16z.use_theme()   # apply globally once

    fig, ax = a16z.bar_chart(df, x="category", y="value", title="My Chart")
    fig.savefig("output.png")
"""

from .theme import use_theme, style_axes, add_title, add_source, add_branding
from .palette import (
    PALETTE, BACKGROUND, TEXT_DARK, TEXT_MID, TEXT_LIGHT,
    TEAL, MAROON, GOLD, NAVY, GREEN, LIGHT_BLUE, SALMON,
    PALETTE_DIVERGING, PALETTE_SEQUENTIAL, PALETTE_CATEGORICAL,
)
from .bar     import bar_chart
from .line    import line_chart
from .area    import area_chart
from .scatter import scatter_chart
from .pie     import donut_chart
from .table   import table_chart
from .combo   import combo_chart

__all__ = [
    "use_theme", "style_axes", "add_title", "add_source", "add_branding",
    "PALETTE", "BACKGROUND", "TEXT_DARK", "TEXT_MID", "TEXT_LIGHT",
    "TEAL", "MAROON", "GOLD", "NAVY", "GREEN", "LIGHT_BLUE", "SALMON",
    "PALETTE_DIVERGING", "PALETTE_SEQUENTIAL", "PALETTE_CATEGORICAL",
    "bar_chart", "line_chart", "area_chart", "scatter_chart",
    "donut_chart", "table_chart", "combo_chart",
]
