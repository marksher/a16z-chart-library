"""
Scatter / bubble chart — single series or categorical color coding.
"""

from __future__ import annotations

from typing import Optional
import pandas as pd
import plotly.graph_objects as go

from ..themes.base import load_theme
from ..utils.layout import _apply_theme


def scatter(
    data,
    x: str,
    y: str,
    title: str = "",
    subtitle: str = None,
    source: str = None,
    size_col: Optional[str] = None,
    color_col: Optional[str] = None,
    label_col: Optional[str] = None,
    theme="a16z-news",
    width: int = 900,
    height: int = 560,
) -> go.Figure:
    """
    Scatter or bubble chart.

    Parameters
    ----------
    data      : pd.DataFrame or list-of-dicts
    x         : column name for x-axis
    y         : column name for y-axis
    size_col  : column name whose values scale marker size (bubble chart)
    color_col : column name for categorical coloring (one color per category)
    label_col : column name for point labels (annotated next to markers)
    theme     : 'a16z-news' | path to YAML | Theme object | None

    Returns
    -------
    plotly.graph_objects.Figure
    """
    df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data.copy()
    if df.empty:
        raise ValueError("data is empty — pass a DataFrame with at least one row")

    for col in [x, y]:
        if col not in df.columns:
            raise ValueError(f"column '{col}' not found. Available: {list(df.columns)}")

    t = load_theme(theme)
    palette = t.palette if t else None

    marker_size_base = t.scatter.get("marker_size", 8) if t else 8
    opacity = t.scatter.get("opacity", 0.8) if t else 0.8

    label_font = dict(
        size=t.font_sizes.get("data_label", 9) if t else 9,
        family=t.fonts["family"] if t else None,
    )

    fig = go.Figure()

    if color_col and color_col in df.columns:
        categories = df[color_col].unique()
        for i, cat in enumerate(categories):
            mask = df[color_col] == cat
            sub = df[mask]
            color = palette[i % len(palette)] if palette else None

            sizes = (
                sub[size_col].tolist() if size_col and size_col in sub.columns
                else marker_size_base
            )

            fig.add_trace(go.Scatter(
                x=sub[x],
                y=sub[y],
                name=str(cat),
                mode="markers+text" if label_col else "markers",
                text=sub[label_col].tolist() if label_col and label_col in sub.columns else None,
                textposition="top center",
                textfont={**label_font, "color": color},
                marker=dict(
                    color=color,
                    size=sizes,
                    opacity=opacity,
                    line=dict(width=0),
                ),
            ))
    else:
        color = palette[0] if palette else None
        sizes = (
            df[size_col].tolist() if size_col and size_col in df.columns
            else marker_size_base
        )

        fig.add_trace(go.Scatter(
            x=df[x],
            y=df[y],
            name="",
            mode="markers+text" if label_col else "markers",
            text=df[label_col].tolist() if label_col and label_col in df.columns else None,
            textposition="top center",
            textfont={**label_font, "color": color},
            marker=dict(
                color=color,
                size=sizes,
                opacity=opacity,
                line=dict(width=0),
            ),
            showlegend=False,
        ))

    return _apply_theme(fig, t, title, subtitle, source, width, height)
