"""
Big number — prominent single metric display.

Shows a large number with an optional label underneath.
Simpler than stat_card — no header banner, just the value.
"""

from __future__ import annotations

from typing import Union

import plotly.graph_objects as go

from ..themes.base import load_theme


def big_number(
    value: Union[str, int, float],
    label: str = "",
    theme="news",
    width: int = 250,
    height: int = 150,
) -> go.Figure:
    """
    Large single-metric display.

    Parameters
    ----------
    value  : the number or text to display prominently
    label  : optional label below the value
    theme  : 'news' | path to YAML | Theme object | None
    width  : figure width in pixels
    height : figure height in pixels

    Returns
    -------
    plotly.graph_objects.Figure
    """
    t = load_theme(theme)

    if t:
        palette = t.palette
        bg = t.background
        font_family = t.fonts["family"]
        subtitle_color = t.text["subtitle"]
        cfg = t.big_number
    else:
        palette = ["#1C2B3A"]
        bg = "#FFFFFF"
        font_family = "Arial, sans-serif"
        subtitle_color = "#666666"
        cfg = {}

    value_color = cfg.get("value_color") or palette[0]
    value_font_size = cfg.get("value_font_size", 56)
    label_font_size = cfg.get("label_font_size", 13)

    fig = go.Figure()

    # Hide axes
    fig.update_xaxes(visible=False, range=[0, 1])
    fig.update_yaxes(visible=False, range=[0, 1])

    # Position value higher if there's a label, centered if not
    value_y = 0.58 if label else 0.5

    fig.add_annotation(
        x=0.5, y=value_y,
        xref="paper", yref="paper",
        text=f"<b>{value}</b>",
        showarrow=False,
        font=dict(
            size=value_font_size,
            family=font_family,
            color=value_color,
        ),
        xanchor="center",
        yanchor="middle",
    )

    if label:
        fig.add_annotation(
            x=0.5, y=0.22,
            xref="paper", yref="paper",
            text=label,
            showarrow=False,
            font=dict(
                size=label_font_size,
                family=font_family,
                color=subtitle_color,
            ),
            xanchor="center",
            yanchor="middle",
        )

    fig.update_layout(
        width=width,
        height=height,
        margin=dict(t=8, b=8, l=8, r=8),
        paper_bgcolor=bg,
        plot_bgcolor=bg,
        showlegend=False,
    )

    return fig
