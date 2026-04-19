"""
Sparkline variants — stripped-down mini charts for inline / small-space use.

No axes, no title, no legend. Just the shape.
Useful in tables, dashboards, or anywhere a full chart is too heavy.

  sparkline_line  — line trend
  sparkline_area  — filled area trend
  sparkline_bar   — bar column trend
"""

from __future__ import annotations

from typing import Union
import pandas as pd
import plotly.graph_objects as go

from ..themes.base import load_theme


def _spark_layout(fig: go.Figure, bg: str, width: int, height: int) -> go.Figure:
    """Apply minimal no-decoration layout common to all sparkline variants."""
    fig.update_layout(
        width=width,
        height=height,
        margin=dict(t=4, b=4, l=4, r=4),
        paper_bgcolor=bg,
        plot_bgcolor=bg,
        showlegend=False,
    )
    fig.update_xaxes(visible=False, showgrid=False, zeroline=False)
    fig.update_yaxes(visible=False, showgrid=False, zeroline=False)
    return fig


def sparkline_line(
    data,
    x: str,
    y: Union[str, list],
    end_dot: bool = True,
    theme="default",
    width: int = 200,
    height: int = 60,
) -> go.Figure:
    """
    Minimal sparkline — line only, no decorations.

    Parameters
    ----------
    data     : pd.DataFrame or list-of-dicts
    x        : column name for x-axis values (not displayed)
    y        : column name or list of names for the line(s)
    end_dot  : show a filled dot at the last data point
    theme    : 'default' | path to YAML | Theme object | None
    """
    df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data.copy()
    if df.empty:
        raise ValueError("data is empty")

    t = load_theme(theme)
    palette = t.palette if t else ["#1C2B3A"]
    bg = t.background if t else "#FFFFFF"
    line_w = t.line.get("width", 2) if t else 2

    y_cols = [y] if isinstance(y, str) else list(y)
    fig = go.Figure()

    for i, col in enumerate(y_cols):
        color = palette[i % len(palette)]
        vals = list(df[col])
        n = len(vals)
        sizes = [0] * (n - 1) + [5] if (end_dot and n > 0) else [0] * n

        fig.add_trace(go.Scatter(
            x=df[x], y=vals,
            mode="lines+markers",
            line=dict(color=color, width=line_w),
            marker=dict(color=color, size=sizes),
            showlegend=False,
        ))

    return _spark_layout(fig, bg, width, height)


def sparkline_area(
    data,
    x: str,
    y: Union[str, list],
    opacity: float = 0.6,
    theme="default",
    width: int = 200,
    height: int = 60,
) -> go.Figure:
    """
    Minimal sparkline — filled area, no decorations.

    Parameters
    ----------
    data    : pd.DataFrame or list-of-dicts
    x       : column name for x-axis values (not displayed)
    y       : column name or list of names for the area(s)
    opacity : fill opacity (0–1)
    theme   : 'default' | path to YAML | Theme object | None
    """
    df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data.copy()
    if df.empty:
        raise ValueError("data is empty")

    t = load_theme(theme)
    palette = t.palette if t else ["#1C2B3A"]
    bg = t.background if t else "#FFFFFF"
    line_w = t.line.get("width", 1.5) if t else 1.5

    y_cols = [y] if isinstance(y, str) else list(y)
    fig = go.Figure()

    for i, col in enumerate(y_cols):
        color = palette[i % len(palette)]
        fig.add_trace(go.Scatter(
            x=df[x], y=df[col],
            mode="lines",
            fill="tozeroy",
            line=dict(color=color, width=line_w),
            fillcolor=_hex_opacity(color, opacity),
            showlegend=False,
        ))

    return _spark_layout(fig, bg, width, height)


def sparkline_bar(
    data,
    x: str,
    y: Union[str, list],
    theme="default",
    width: int = 200,
    height: int = 60,
) -> go.Figure:
    """
    Minimal sparkline — bar columns, no decorations.

    Parameters
    ----------
    data  : pd.DataFrame or list-of-dicts
    x     : column name for x-axis values (not displayed)
    y     : column name or list of names for the bar(s)
    theme : 'default' | path to YAML | Theme object | None
    """
    df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data.copy()
    if df.empty:
        raise ValueError("data is empty")

    t = load_theme(theme)
    palette = t.palette if t else ["#1C2B3A"]
    bg = t.background if t else "#FFFFFF"

    y_cols = [y] if isinstance(y, str) else list(y)
    fig = go.Figure()

    for i, col in enumerate(y_cols):
        color = palette[i % len(palette)]
        fig.add_trace(go.Bar(
            x=df[x], y=df[col],
            marker_color=color,
            showlegend=False,
        ))

    if len(y_cols) > 1:
        fig.update_layout(barmode="group", bargap=0.15, bargroupgap=0.05)
    else:
        fig.update_layout(bargap=0.2)

    return _spark_layout(fig, bg, width, height)


# Keep the original name as an alias for backward compatibility
sparkline = sparkline_line


def _hex_opacity(hex_color: str, alpha: float) -> str:
    """Convert '#RRGGBB' to 'rgba(r,g,b,a)' string."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"
