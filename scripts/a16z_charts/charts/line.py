"""
Line chart — single or multi-series, with optional end-of-line labels.
"""

from __future__ import annotations

from typing import Union
import pandas as pd
import plotly.graph_objects as go

from ..themes.base import load_theme
from ..utils.layout import _apply_theme


def line(
    data,
    x: str,
    y: Union[str, list],
    title: str = "",
    subtitle: str = None,
    source: str = None,
    dashed: list = None,
    end_labels: bool = None,
    theme="a16z-news",
    width: int = 900,
    height: int = 560,
) -> go.Figure:
    """
    Line chart.

    Parameters
    ----------
    data        : pd.DataFrame or list-of-dicts
    x           : column name for the x-axis (dates, categories, …)
    y           : column name or list of series names
    dashed      : list of series names to render as dashed lines
    end_labels  : True = inline label at each line's last point (overrides theme)
                  False = use legend instead
    theme       : 'a16z-news' | path to YAML | Theme object | None

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

    dashed = dashed or []

    # Resolve end_labels setting
    use_end_labels = end_labels
    if use_end_labels is None:
        use_end_labels = t.line.get("end_labels", True) if t else False
    # Only apply end labels when there are multiple series
    use_end_labels = use_end_labels and len(y_cols) > 1

    line_width = t.line.get("width", 2.5) if t else 2.0
    use_markers = t.line.get("markers", False) if t else False
    marker_size = t.line.get("marker_size", 6) if t else 6

    fig = go.Figure()

    for i, col in enumerate(y_cols):
        color = palette[i % len(palette)] if palette else None
        is_dashed = col in dashed
        mode = "lines+markers" if use_markers else "lines"

        fig.add_trace(go.Scatter(
            x=df[x],
            y=df[col],
            name=col,
            mode=mode,
            line=dict(
                color=color,
                width=line_width,
                dash="dot" if is_dashed else "solid",
            ),
            marker=dict(
                size=marker_size,
                color=color,
            ),
            showlegend=not use_end_labels,
        ))

    # End-of-line labels
    if use_end_labels:
        extra_right = 0
        for i, col in enumerate(y_cols):
            color = palette[i % len(palette)] if palette else "#333"
            last_x = df[x].iloc[-1]
            last_y = df[col].iloc[-1]

            label = f"{col} {last_y:+.0f}%" if "%" in col else col
            label = col  # keep it simple

            fig.add_annotation(
                x=last_x,
                y=last_y,
                text=f" {col}",
                showarrow=False,
                xanchor="left",
                font=dict(
                    size=t.font_sizes.get("data_label", 9) if t else 9,
                    color=color,
                    family=t.fonts["family"] if t else None,
                ),
            )
            # Estimate label width to expand right margin
            extra_right = max(extra_right, len(col) * 7 + 12)

        # Extend right margin to prevent labels from being clipped
        if t:
            fig.update_layout(
                margin_r=max(t.margins.get("right", 50), extra_right)
            )

    return _apply_theme(fig, t, title, subtitle, source, width, height)
