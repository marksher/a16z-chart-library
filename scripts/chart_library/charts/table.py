"""
Data table chart.

Design note: uses the same universal title / subtitle / source / branding
treatment as all other chart types, enforcing stiff visual consistency.
"""

from __future__ import annotations

from typing import Optional, List
import pandas as pd
import plotly.graph_objects as go

from ..themes.base import load_theme
from ..utils.layout import _apply_theme


def table(
    data,
    title: str = "",
    subtitle: str = None,
    source: str = None,
    highlight_rows: List[int] = None,
    header_cols: List[str] = None,
    theme="news",
    width: int = 900,
    height: Optional[int] = None,
) -> go.Figure:
    """
    Data table.

    Parameters
    ----------
    data          : pd.DataFrame or list-of-dicts
    highlight_rows: list of row indices (0-based) to highlight in gold
    header_cols   : column names to display; defaults to all columns
    theme         : 'news' | path to YAML | Theme object | None

    Returns
    -------
    plotly.graph_objects.Figure
    """
    df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data.copy()
    if df.empty:
        raise ValueError("data is empty — pass a DataFrame with at least one row")

    t = load_theme(theme)
    highlight_rows = highlight_rows or []
    cols = header_cols if header_cols is not None else list(df.columns)

    for col in cols:
        if col not in df.columns:
            raise ValueError(f"column '{col}' not found. Available: {list(df.columns)}")

    # Colors
    bg = t.background if t else "white"
    hi = t.table.get("highlight_color", "#C4A575") if t else "#C4A575"
    border = t.table.get("border_color", "#E0DAD0") if t else "#E0DAD0"
    header_bg = t.table.get("header_background", "#1C2B3A") if t else "#1C2B3A"
    header_fg = t.table.get("header_text", "#FFFFFF") if t else "#FFFFFF"
    cell_fg = t.text.get("label", "#5A6472") if t else "#5A6472"

    n_rows = len(df)
    row_colors = [hi if i in highlight_rows else bg for i in range(n_rows)]
    # Plotly Table colors cells column-by-column, so repeat per column
    cell_fill = [row_colors for _ in cols]

    cell_values = [df[col].tolist() for col in cols]

    header_font = dict(
        family=t.fonts["family"] if t else "serif",
        size=t.font_sizes.get("axis_label", 11) if t else 11,
        color=header_fg,
    )
    cell_font = dict(
        family=t.fonts["family"] if t else "serif",
        size=t.font_sizes.get("axis_tick", 10) if t else 10,
        color=cell_fg,
    )

    fig = go.Figure(go.Table(
        header=dict(
            values=[f"<b>{c}</b>" for c in cols],
            fill_color=header_bg,
            font=header_font,
            align="left",
            line_color=border,
            line_width=1,
            height=30,
        ),
        cells=dict(
            values=cell_values,
            fill_color=cell_fill,
            font=cell_font,
            align="left",
            line_color=border,
            line_width=1,
            height=26,
        ),
    ))

    # Auto-size height to fit content when not specified
    if height is None:
        height = min(80 + n_rows * 28 + 120, 900)

    # Tables have no axes or legend — suppress them
    fig.update_layout(showlegend=False)

    return _apply_theme(fig, t, title, subtitle, source, width, height)
