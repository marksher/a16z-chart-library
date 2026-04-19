"""
Diverging bar chart — horizontal bars for positive/negative values.

Typical use: percent change rankings (cities, countries, products).
Bars extend right for positive values, left for negative.
"""

from __future__ import annotations

from typing import Optional
import pandas as pd
import plotly.graph_objects as go

from ..themes.base import load_theme
from ..utils.layout import _apply_theme


def diverging_bar(
    data,
    y: str,
    x: str,
    title: str = "",
    subtitle: Optional[str] = None,
    source: Optional[str] = None,
    label_format: Optional[str] = None,
    positive_label: Optional[str] = None,
    negative_label: Optional[str] = None,
    sorted: bool = True,
    theme="news",
    width: int = 700,
    height: int = 800,
) -> go.Figure:
    """
    Horizontal diverging bar chart for positive/negative comparisons.

    Parameters
    ----------
    data             : pd.DataFrame or list-of-dicts
    y                : column name for categories (y-axis)
    x                : column name for values (positive or negative numbers)
    label_format     : format string for bar labels, e.g. "{:+.0f}%".
                       Defaults to auto: "+N%" / "−N%"
    positive_label   : legend entry for positive bars (None = no legend)
    negative_label   : legend entry for negative bars (None = no legend)
    sorted           : sort categories by value (largest at top)
    theme            : 'news' | path to YAML | Theme object | None

    Returns
    -------
    plotly.graph_objects.Figure
    """
    df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data.copy()
    if df.empty:
        raise ValueError("data is empty")

    if y not in df.columns:
        raise ValueError(f"y column '{y}' not found. Available: {list(df.columns)}")
    if x not in df.columns:
        raise ValueError(f"x column '{x}' not found. Available: {list(df.columns)}")

    if sorted:
        df = df.sort_values(x, ascending=True)  # ascending=True → largest at top of horizontal chart

    t = load_theme(theme)
    palette = t.palette if t else ["#1C2B3A", "#4A7C59"]

    neg_color = palette[0]
    pos_color = palette[1] if len(palette) > 1 else palette[0]

    bar_colors = [pos_color if v >= 0 else neg_color for v in df[x]]

    if label_format:
        texts = [label_format.format(v) for v in df[x]]
    else:
        texts = [f"+{v:.0f}%" if v >= 0 else f"\u2212{abs(v):.0f}%" for v in df[x]]

    data_label_font = dict(
        size=t.font_sizes.get("data_label", 9) if t else 9,
        color=t.text["label"] if t else None,
        family=t.fonts["family"] if t else None,
    )

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df[y],
        x=df[x],
        orientation="h",
        marker_color=bar_colors,
        text=texts,
        textposition="outside",
        textfont=data_label_font,
        showlegend=False,
        cliponaxis=False,
    ))

    # Optional legend swatches
    if positive_label:
        fig.add_trace(go.Bar(
            y=[None], x=[None],
            orientation="h",
            marker_color=pos_color,
            name=positive_label,
            showlegend=True,
        ))
    if negative_label:
        fig.add_trace(go.Bar(
            y=[None], x=[None],
            orientation="h",
            marker_color=neg_color,
            name=negative_label,
            showlegend=True,
        ))

    fig.update_layout(barmode="relative")

    if t:
        fig.update_layout(bargap=t.bar.get("gap", 0.35))

    # Prominent zero line
    zero_color = t.text["title"] if t else "#1C2B3A"
    fig.update_xaxes(
        zeroline=True,
        zerolinecolor=zero_color,
        zerolinewidth=1.5,
        autorange=True,
    )

    fig.update_yaxes(automargin=True)

    return _apply_theme(fig, t, title, subtitle, source, width, height)
