"""
Gauge — semicircular dial chart with a colored header banner.

Displays a value on a half-circle arc with min/max labels.
Useful for KPIs like rates, scores, and percentages.
"""

from __future__ import annotations

import math
from typing import Optional, Union

import plotly.graph_objects as go

from ..themes.base import load_theme


def gauge(
    value: Union[int, float],
    label: str = "",
    min_val: float = 0,
    max_val: float = 100,
    value_format: Optional[str] = None,
    theme="news",
    width: int = 300,
    height: int = 280,
) -> go.Figure:
    """
    Semicircular gauge dial with colored header banner.

    Parameters
    ----------
    value        : the current metric value
    label        : header banner text (e.g. "No Show Rate")
    min_val      : minimum scale value (left end of arc)
    max_val      : maximum scale value (right end of arc)
    value_format : format string for displayed value, e.g. "{:.0f}%".
                   Defaults to auto: appends "%" if max_val == 100.
    theme        : 'news' | path to YAML | Theme object | None
    width        : figure width in pixels
    height       : figure height in pixels

    Returns
    -------
    plotly.graph_objects.Figure
    """
    t = load_theme(theme)

    if t:
        palette = t.palette
        bg = t.background
        font_family = t.fonts["family"]
        title_color = t.text["title"]
        subtitle_color = t.text["subtitle"]
        axis_color = t.text["axis"]
        border_color = t.spines.get("color", "#C8C0B4")
        cfg = t.gauge if hasattr(t, "gauge") and isinstance(t.gauge, dict) else {}
    else:
        palette = ["#1C2B3A"]
        bg = "#FFFFFF"
        font_family = "Arial, sans-serif"
        title_color = "#1C2B3A"
        subtitle_color = "#666666"
        axis_color = "#999999"
        border_color = "#CCCCCC"
        cfg = {}

    header_color = cfg.get("header_color") or palette[0]
    arc_bg_color = cfg.get("arc_bg_color", "#E0E0E0")
    arc_fg_color = cfg.get("arc_fg_color") or palette[0]
    value_font_size = cfg.get("value_font_size", 32)
    label_font_size = cfg.get("label_font_size", 13)
    min_max_font_size = cfg.get("min_max_font_size", 11)

    # Format the display value
    if value_format:
        display_val = value_format.format(value)
    elif max_val == 100 and min_val == 0:
        display_val = f"{value:.0f}%" if isinstance(value, float) else f"{value}%"
    else:
        display_val = str(value)

    # Format min/max labels
    if max_val == 100 and min_val == 0:
        min_label = f"{min_val:.0f}%" if isinstance(min_val, float) else f"{min_val}%"
        max_label = f"{max_val:.0f}%" if isinstance(max_val, float) else f"{max_val}%"
    else:
        min_label = str(min_val)
        max_label = str(max_val)

    # Clamp value to range
    clamped = max(min_val, min(value, max_val))
    frac = (clamped - min_val) / (max_val - min_val) if max_val != min_val else 0

    fig = go.Figure()

    # Hide axes — use a square coordinate space
    fig.update_xaxes(visible=False, range=[-1.3, 1.3])
    fig.update_yaxes(visible=False, range=[-0.4, 1.5], scaleanchor="x", scaleratio=1)

    # Header banner fraction (paper coords)
    header_frac = 0.22

    # Card border
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=1, y1=1,
        xref="paper", yref="paper",
        line=dict(color=border_color, width=1.5),
        fillcolor="#FFFFFF",
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

    # Label in header
    if label:
        fig.add_annotation(
            x=0.5, y=1 - header_frac / 2,
            xref="paper", yref="paper",
            text=f"<b>{label}</b>",
            showarrow=False,
            font=dict(size=label_font_size, family=font_family, color="#FFFFFF"),
            xanchor="center", yanchor="middle",
        )

    # ── Draw the gauge arc ───────────────────────────────────────────────────
    # Background arc (full semicircle)
    n_pts = 60
    arc_r = 0.85
    arc_inner = 0.55

    # Background arc path
    bg_path = _arc_path(math.pi, 0, arc_r, arc_inner, n_pts)
    fig.add_shape(
        type="path", path=bg_path,
        fillcolor=arc_bg_color,
        line=dict(width=0),
    )

    # Foreground arc (filled portion)
    if frac > 0.001:
        angle_start = math.pi
        angle_end = math.pi * (1 - frac)
        fg_path = _arc_path(angle_start, angle_end, arc_r, arc_inner, max(3, int(n_pts * frac)))
        fig.add_shape(
            type="path", path=fg_path,
            fillcolor=arc_fg_color,
            line=dict(width=0),
        )

    # Value text (centered below arc)
    fig.add_annotation(
        x=0, y=0.05,
        xref="x", yref="y",
        text=f"<b>{display_val}</b>",
        showarrow=False,
        font=dict(size=value_font_size, family=font_family, color=arc_fg_color),
        xanchor="center", yanchor="middle",
    )

    # Min label (bottom-left of arc)
    fig.add_annotation(
        x=-arc_r, y=-0.15,
        xref="x", yref="y",
        text=min_label,
        showarrow=False,
        font=dict(size=min_max_font_size, family=font_family, color=axis_color),
        xanchor="center", yanchor="top",
    )

    # Max label (bottom-right of arc)
    fig.add_annotation(
        x=arc_r, y=-0.15,
        xref="x", yref="y",
        text=max_label,
        showarrow=False,
        font=dict(size=min_max_font_size, family=font_family, color=axis_color),
        xanchor="center", yanchor="top",
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


def _arc_path(
    angle_start: float,
    angle_end: float,
    r_outer: float,
    r_inner: float,
    n_pts: int,
) -> str:
    """Build an SVG path string for a thick arc segment."""
    # Outer arc (start → end)
    outer = []
    for i in range(n_pts + 1):
        a = angle_start + (angle_end - angle_start) * i / n_pts
        outer.append((r_outer * math.cos(a), r_outer * math.sin(a)))

    # Inner arc (end → start, reversed)
    inner = []
    for i in range(n_pts + 1):
        a = angle_end + (angle_start - angle_end) * i / n_pts
        inner.append((r_inner * math.cos(a), r_inner * math.sin(a)))

    parts = [f"M {outer[0][0]:.4f} {outer[0][1]:.4f}"]
    for x, y in outer[1:]:
        parts.append(f"L {x:.4f} {y:.4f}")
    for x, y in inner:
        parts.append(f"L {x:.4f} {y:.4f}")
    parts.append("Z")

    return " ".join(parts)
