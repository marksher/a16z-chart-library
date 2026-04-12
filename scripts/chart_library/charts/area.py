"""
Area chart — single fill or stacked multi-series.
"""

from __future__ import annotations

from typing import Union
import pandas as pd
import plotly.graph_objects as go

from ..themes.base import load_theme
from ..utils.layout import _apply_theme, _hex_to_rgba


def area(
    data,
    x: str,
    y: Union[str, list],
    title: str = "",
    subtitle: str = None,
    source: str = None,
    stacked: bool = True,
    theme="a16z-news",
    width: int = 900,
    height: int = 560,
) -> go.Figure:
    """
    Area chart.

    Parameters
    ----------
    data    : pd.DataFrame or list-of-dicts
    x       : column name for x-axis
    y       : column name (single) or list of series names (stacked)
    stacked : True = stacked area; False = overlapping fills to zero
    theme   : 'a16z-news' | path to YAML | Theme object | None

    Returns
    -------
    plotly.graph_objects.Figure
    """
    df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data.copy()
    if df.empty:
        raise ValueError("data is empty — pass a DataFrame with at least one row")

    if x not in df.columns:
        raise ValueError(f"x column '{x}' not found. Available: {list(df.columns)}")

    t = load_theme(theme)
    palette = t.palette if t else None

    y_cols = [y] if isinstance(y, str) else list(y)
    for col in y_cols:
        if col not in df.columns:
            raise ValueError(f"y column '{col}' not found. Available: {list(df.columns)}")

    opacity = t.area.get("opacity", 0.75) if t else 0.75
    line_width = t.area.get("line_width", 0) if t else 1.0

    fig = go.Figure()

    for i, col in enumerate(y_cols):
        color = palette[i % len(palette)] if palette else None
        fill_color = _hex_to_rgba(color, opacity) if color else None

        fig.add_trace(go.Scatter(
            x=df[x],
            y=df[col],
            name=col,
            mode="lines",
            stackgroup="one" if stacked else None,
            fill="tozeroy" if not stacked else None,
            fillcolor=fill_color,
            line=dict(
                color=color,
                width=line_width,
            ),
            showlegend=True,
        ))

    return _apply_theme(fig, t, title, subtitle, source, width, height)
