"""
Pie / donut chart.

Design note: even though pie charts have no axes, _apply_theme() still
enforces the universal visual identity — same background, title treatment,
font family, source attribution, and branding as every other chart type.
"""

from __future__ import annotations

from typing import Optional
import pandas as pd
import plotly.graph_objects as go

from ..themes.base import load_theme
from ..utils.layout import _apply_theme


def pie(
    data,
    labels: str,
    values: str,
    title: str = "",
    subtitle: str = None,
    source: str = None,
    hole: Optional[float] = None,
    theme="default",
    width: int = 700,
    height: int = 560,
) -> go.Figure:
    """
    Pie or donut chart.

    Parameters
    ----------
    data   : pd.DataFrame or list-of-dicts
    labels : column name for slice labels
    values : column name for slice values
    hole   : donut hole size 0.0–0.9 (overrides theme default; 0 = full pie)
    theme  : 'default' | path to YAML | Theme object | None

    Returns
    -------
    plotly.graph_objects.Figure
    """
    df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data.copy()
    if df.empty:
        raise ValueError("data is empty — pass a DataFrame with at least one row")

    for col in [labels, values]:
        if col not in df.columns:
            raise ValueError(f"column '{col}' not found. Available: {list(df.columns)}")

    t = load_theme(theme)
    palette = t.palette if t else None

    hole_size = hole
    if hole_size is None:
        hole_size = t.pie.get("hole", 0.55) if t else 0.0

    bg = t.background if t else "white"
    n = len(df)
    colors = (palette * ((n // len(palette)) + 1))[:n] if palette else None

    fig = go.Figure(go.Pie(
        labels=df[labels],
        values=df[values],
        hole=hole_size,
        marker=dict(
            colors=colors,
            line=dict(color=bg, width=2),
        ),
        textfont=dict(
            family=t.fonts["family"] if t else "serif",
            size=t.font_sizes.get("data_label", 10) if t else 10,
        ),
        textinfo="percent+label",
        insidetextorientation="auto",
        # Legend replaces the text labels when there are many slices
        showlegend=True,
    ))

    # Override Plotly's default right-side legend to match all other chart types
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.12,
            xanchor="center",
            x=0.5,
        )
    )

    return _apply_theme(fig, t, title, subtitle, source, width, height)
