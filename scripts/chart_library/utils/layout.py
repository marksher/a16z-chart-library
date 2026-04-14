"""
Core theme-application function and PNG export helper.

Every chart function calls _apply_theme() as its final step.
This is where all cross-type visual consistency is enforced:
background, title treatment, font family, source attribution,
branding, legend position, grid, spines.
"""

from __future__ import annotations

from typing import Optional

import plotly.graph_objects as go

from ..themes.base import Theme


def _apply_theme(
    fig: go.Figure,
    theme: Optional[Theme],
    title: str,
    subtitle: Optional[str],
    source: Optional[str],
    width: int,
    height: int,
) -> go.Figure:
    """
    Apply *theme* to *fig* in-place and return it.

    When *theme* is None the figure is returned with only width/height
    set, using Plotly's own defaults for everything else.
    """
    fig.update_layout(width=width, height=height)

    if theme is None:
        # Plotly defaults — just honour the size
        return fig

    t = theme

    # ── Global layout ─────────────────────────────────────────────────────────
    fig.update_layout(
        paper_bgcolor=t.background,
        plot_bgcolor=t.plot_background,
        # Global font is the fallback; individual elements override below
        font=dict(
            family=t.fonts["family"],
            color=t.text["axis"],
            size=t.font_sizes["axis_tick"],
        ),
        margin=dict(
            t=t.margins["top"],
            b=t.margins["bottom"],
            l=t.margins["left"],
            r=t.margins["right"],
        ),
        # Set colorway so all auto-colored traces use the theme palette
        colorway=t.palette,
        # Clear Plotly's own title — we render it as an annotation
        title_text="",
        showlegend=True,
        legend=dict(
            orientation=t.legend.get("orientation", "h"),
            yanchor="top",
            y=-0.12,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(
                family=t.fonts["family"],
                size=t.font_sizes["axis_tick"],
                color=t.text["label"],
            ),
        ),
    )

    # ── Axes (safe to set for all chart types; ignored on pie/table/map) ──────
    h_grid = t.grid.get("horizontal", True)
    v_grid = t.grid.get("vertical", False)
    spine_color = t.spines.get("color", "#C8C0B4")
    spine_width = t.spines.get("width", 1)

    fig.update_xaxes(
        showgrid=v_grid,
        gridcolor=t.grid["color"],
        gridwidth=t.grid["width"],
        zeroline=False,
        showline=True,
        linecolor=spine_color,
        linewidth=spine_width,
        mirror=False,
        showspikes=False,
        automargin=True,
        tickfont=dict(
            family=t.fonts["family"],
            color=t.text["axis"],
            size=t.font_sizes["axis_tick"],
        ),
        title_font=dict(
            family=t.fonts["family"],
            color=t.text["label"],
            size=t.font_sizes.get("axis_label", 11),
        ),
    )

    fig.update_yaxes(
        showgrid=h_grid,
        gridcolor=t.grid["color"],
        gridwidth=t.grid["width"],
        zeroline=False,
        showline=False,
        showspikes=False,
        automargin=True,
        tickfont=dict(
            family=t.fonts["family"],
            color=t.text["axis"],
            size=t.font_sizes["axis_tick"],
        ),
        title_font=dict(
            family=t.fonts["family"],
            color=t.text["label"],
            size=t.font_sizes.get("axis_label", 11),
        ),
    )

    # ── Title + subtitle (paper-coordinate annotations) ───────────────────────
    # yshift is in pixels relative to y=1 (top of plot area).
    # With margin.top=90 there is 90 px above the plot area for these texts.
    if title:
        title_yshift = 75 if subtitle else 30
        fig.add_annotation(
            x=0, y=1,
            xref="paper", yref="paper",
            text=f"<b>{title}</b>",
            showarrow=False,
            xanchor="left",
            yanchor="bottom",
            yshift=title_yshift,
            font=dict(
                size=t.font_sizes["title"],
                family=t.fonts["family"],
                color=t.text["title"],
            ),
        )

    if subtitle:
        fig.add_annotation(
            x=0, y=1,
            xref="paper", yref="paper",
            text=subtitle,
            showarrow=False,
            xanchor="left",
            yanchor="bottom",
            yshift=28,
            font=dict(
                size=t.font_sizes["subtitle"],
                family=t.fonts["family"],
                color=t.text["subtitle"],
            ),
        )

    # ── Source attribution (bottom-left) ──────────────────────────────────────
    if source:
        prefix = t.source.get("prefix", "Source: ")
        text = f"<i>{prefix}{source}</i>" if t.source.get("italic", True) else f"{prefix}{source}"
        fig.add_annotation(
            x=0, y=0,
            xref="paper", yref="paper",
            text=text,
            showarrow=False,
            xanchor="left",
            yanchor="top",
            yshift=-26,
            font=dict(
                size=t.font_sizes["source"],
                family=t.fonts["family"],
                color=t.text["source"],
            ),
        )

    # ── Branding (bottom-right) ───────────────────────────────────────────────
    if t.branding.get("show", True):
        image_path = t.branding.get("image")
        if image_path:
            # Resolve local file → base64 data URI; URLs pass through as-is
            import base64 as _b64
            from pathlib import Path as _P
            p = _P(image_path)
            if p.exists():
                ext = p.suffix.lower().lstrip(".")
                mime = {
                    "svg": "image/svg+xml",
                    "png": "image/png",
                    "jpg": "image/jpeg",
                    "jpeg": "image/jpeg",
                }.get(ext, "image/png")
                src = f"data:{mime};base64,{_b64.b64encode(p.read_bytes()).decode()}"
            else:
                src = image_path  # treat as URL

            # sizex/sizey are paper fractions relative to the plot area;
            # convert the pixel spec using the figure's plot-area dimensions.
            plot_w = width - t.margins.get("left", 60) - t.margins.get("right", 50)
            plot_h = height - t.margins.get("top", 90) - t.margins.get("bottom", 60)
            sizex = t.branding.get("image_width", 60) / max(plot_w, 1)
            sizey = t.branding.get("image_height", 20) / max(plot_h, 1)

            fig.add_layout_image(
                source=src,
                xref="paper", yref="paper",
                x=1, y=0,
                xanchor="right", yanchor="top",
                sizex=sizex,
                sizey=sizey,
                sizing="contain",
                opacity=t.branding.get("opacity", 1.0),
                layer="above",
            )
        else:
            fig.add_annotation(
                x=1, y=0,
                xref="paper", yref="paper",
                text=f"<b>{t.branding['text']}</b>",
                showarrow=False,
                xanchor="right",
                yanchor="top",
                yshift=-26,
                font=dict(
                    size=t.branding["font_size"],
                    family=t.fonts["family"],
                    color=t.branding["color"],
                ),
            )

    return fig


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert '#RRGGBB' to 'rgba(r,g,b,a)' string."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def save_svg(fig: go.Figure, path: str) -> None:
    """
    Export *fig* as a vector SVG at *path*.

    Requires kaleido: pip install kaleido

    Parameters
    ----------
    fig   : plotly Figure
    path  : output file path, e.g. "chart.svg"
    """
    try:
        fig.write_image(path, format="svg")
    except Exception as exc:
        if "kaleido" in str(exc).lower() or "orca" in str(exc).lower():
            raise RuntimeError(
                "SVG export requires kaleido. Install with: pip install kaleido"
            ) from exc
        raise


def save_png(fig: go.Figure, path: str, scale: int = 2) -> None:
    """
    Export *fig* as a static PNG at *path*.

    Requires kaleido: pip install kaleido

    Parameters
    ----------
    fig   : plotly Figure
    path  : output file path, e.g. "chart.png"
    scale : pixel multiplier; scale=2 doubles the width/height for retina output
    """
    try:
        fig.write_image(path, scale=scale)
    except Exception as exc:
        if "kaleido" in str(exc).lower() or "orca" in str(exc).lower():
            raise RuntimeError(
                "PNG export requires kaleido. Install with: pip install kaleido"
            ) from exc
        raise
