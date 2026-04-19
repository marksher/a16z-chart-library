"""
Stat card — KPI card with a colored header banner and a large number.

Displays a label in a colored header bar and a prominent value below.
Useful for dashboards, summary panels, and report headers.
"""

from __future__ import annotations

from typing import Union

import plotly.graph_objects as go

from ..themes.base import load_theme


def stat_card(
    value: Union[str, int, float],
    label: str = "",
    theme="default",
    width: int = 300,
    height: int = 200,
) -> go.Figure:
    """
    KPI stat card with colored header banner and large value.

    Parameters
    ----------
    value  : the number or text to display prominently
    label  : header banner text (e.g. "Caregivers", "Active Users")
    theme  : 'default' | path to YAML | Theme object | None
    width  : figure width in pixels
    height : figure height in pixels

    Returns
    -------
    plotly.graph_objects.Figure
    """
    t = load_theme(theme)

    # Theme-derived defaults
    if t:
        palette = t.palette
        bg = t.background
        font_family = t.fonts["family"]
        title_color = t.text["title"]
        border_color = t.spines.get("color", "#C8C0B4")
        cfg = t.stat_card
    else:
        palette = ["#1C2B3A"]
        bg = "#FFFFFF"
        font_family = "Arial, sans-serif"
        title_color = "#1C2B3A"
        border_color = "#CCCCCC"
        cfg = {}

    header_color = cfg.get("header_color") or palette[0]
    value_font_size = cfg.get("value_font_size", 48)
    label_font_size = cfg.get("label_font_size", 14)
    border_radius = cfg.get("border_radius", 12)

    # Header occupies the top ~30% of the card
    header_frac = 0.32

    fig = go.Figure()

    # Hide axes
    fig.update_xaxes(visible=False, range=[0, 1])
    fig.update_yaxes(visible=False, range=[0, 1])

    # Card border (rounded rect)
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=1, y1=1,
        xref="paper", yref="paper",
        line=dict(color=border_color, width=1.5),
        fillcolor="#FFFFFF" if t else "#FFFFFF",
        layer="below",
    )

    # Header banner
    fig.add_shape(
        type="rect",
        x0=0, y0=1 - header_frac, x1=1, y1=1,
        xref="paper", yref="paper",
        fillcolor=header_color,
        line=dict(width=0),
        layer="below",
    )

    # Label text in header
    if label:
        fig.add_annotation(
            x=0.5, y=1 - header_frac / 2,
            xref="paper", yref="paper",
            text=f"<b>{label}</b>",
            showarrow=False,
            font=dict(
                size=label_font_size,
                family=font_family,
                color="#FFFFFF",
            ),
            xanchor="center",
            yanchor="middle",
        )

    # Large value in card body
    body_center_y = (1 - header_frac) / 2
    fig.add_annotation(
        x=0.5, y=body_center_y,
        xref="paper", yref="paper",
        text=f"<b>{value}</b>",
        showarrow=False,
        font=dict(
            size=value_font_size,
            family=font_family,
            color=title_color,
        ),
        xanchor="center",
        yanchor="middle",
    )

    fig.update_layout(
        width=width,
        height=height,
        margin=dict(t=8, b=8, l=8, r=8),
        paper_bgcolor=bg,
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )

    return fig
