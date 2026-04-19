"""
Bar / column chart — horizontal and vertical, single and grouped/stacked.
"""

from __future__ import annotations

from typing import Union
import pandas as pd
import plotly.graph_objects as go

from ..themes.base import load_theme
from ..utils.layout import _apply_theme


def bar(
    data,
    x: str,
    y: Union[str, list],
    title: str = "",
    subtitle: str = None,
    source: str = None,
    orientation: str = "v",
    stacked: bool = False,
    show_values: bool = True,
    theme="default",
    width: int = 900,
    height: int = 560,
) -> go.Figure:
    """
    Bar or column chart.

    Parameters
    ----------
    data        : pd.DataFrame or list-of-dicts
    x           : column name for categories (or values for horizontal bars)
    y           : column name (single series) or list of names (grouped/stacked)
    orientation : 'v' vertical columns | 'h' horizontal bars
    stacked     : True for stacked bars, False for grouped
    show_values : annotate each bar with its value
    theme       : 'default' | path to YAML | Theme object | None (Plotly default)

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

    fig = go.Figure()

    data_label_font = dict(
        size=t.font_sizes.get("data_label", 9) if t else 9,
        color=t.text["label"] if t else None,
        family=t.fonts["family"] if t else None,
    )

    for i, col in enumerate(y_cols):
        color = palette[i % len(palette)] if palette else None
        vals = df[col]
        show = len(y_cols) > 1  # legend only for multi-series

        # Build text labels
        if show_values:
            labels = [
                f"{v:,.0f}" if abs(v) >= 10 else f"{v:.1f}"
                for v in vals
            ]
        else:
            labels = None

        if orientation == "h":
            trace = go.Bar(
                x=vals,
                y=df[x],
                name=col,
                orientation="h",
                marker_color=color,
                text=labels,
                textposition="outside",
                textfont=data_label_font,
                showlegend=show,
                cliponaxis=False,
            )
        else:
            trace = go.Bar(
                x=df[x],
                y=vals,
                name=col,
                marker_color=color,
                text=labels,
                textposition="outside",
                textfont=data_label_font,
                showlegend=show,
                cliponaxis=False,
            )

        fig.add_trace(trace)

    barmode = "stack" if stacked else ("group" if len(y_cols) > 1 else "relative")
    fig.update_layout(barmode=barmode)

    if t:
        bar_cfg = t.bar
        fig.update_layout(
            bargap=bar_cfg.get("gap", 0.25),
            bargroupgap=bar_cfg.get("group_gap", 0.05),
        )

    # Extend clip area so outside-text labels aren't cut off
    if orientation == "h":
        fig.update_xaxes(autorange=True)
    else:
        fig.update_yaxes(autorange=True)

    return _apply_theme(fig, t, title, subtitle, source, width, height)
