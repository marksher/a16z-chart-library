"""
Core theme for the a16z.news chart style.

Usage:
    import a16z_charts as a16z
    a16z.use_theme()          # apply globally once at top of script
    fig, ax = a16z.bar_chart(...)
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from . import palette as pal

# ── rcParams ──────────────────────────────────────────────────────────────────

RCPARAMS = {
    # Figure
    "figure.facecolor":      pal.BACKGROUND,
    "figure.dpi":            150,
    "figure.figsize":        (10, 6),

    # Axes
    "axes.facecolor":        pal.BACKGROUND,
    "axes.edgecolor":        pal.SPINE_COLOR,
    "axes.labelcolor":       pal.TEXT_MID,
    "axes.labelsize":        10,
    "axes.titlesize":        18,
    "axes.titlecolor":       pal.TEXT_DARK,
    "axes.titleweight":      "bold",
    "axes.spines.top":       False,
    "axes.spines.right":     False,

    # Grid
    "axes.grid":             True,
    "axes.grid.axis":        "y",
    "grid.color":            pal.GRID_COLOR,
    "grid.linewidth":        0.6,
    "grid.linestyle":        "-",

    # Ticks
    "xtick.color":           pal.TEXT_LIGHT,
    "ytick.color":           pal.TEXT_LIGHT,
    "xtick.labelsize":       9,
    "ytick.labelsize":       9,
    "xtick.direction":       "out",
    "ytick.direction":       "out",
    "xtick.major.size":      4,
    "ytick.major.size":      4,

    # Lines
    "lines.linewidth":       2.0,
    "lines.solid_capstyle":  "round",

    # Legend
    "legend.frameon":        False,
    "legend.fontsize":       9,
    "legend.labelcolor":     pal.TEXT_MID,
    "legend.loc":            "lower center",

    # Font — Georgia for titles, fallback to serif
    "font.family":           "serif",
    "font.serif":            ["Georgia", "Times New Roman", "DejaVu Serif"],
    "font.size":             10,

    # Save
    "savefig.facecolor":     pal.BACKGROUND,
    "savefig.bbox":          "tight",
    "savefig.dpi":           150,
}


def use_theme():
    """Apply a16z chart style globally."""
    mpl.rcParams.update(RCPARAMS)


# ── Per-axes helpers ──────────────────────────────────────────────────────────

def style_axes(ax):
    """Remove top/right spines, style grid and tick colors."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_edgecolor(pal.SPINE_COLOR)
    ax.spines["bottom"].set_edgecolor(pal.SPINE_COLOR)
    ax.tick_params(colors=pal.TEXT_LIGHT, which="both")
    ax.yaxis.grid(True, color=pal.GRID_COLOR, linewidth=0.6, linestyle="-")
    ax.xaxis.grid(False)
    ax.set_axisbelow(True)
    ax.set_facecolor(pal.BACKGROUND)


def add_title(ax, title, subtitle=None):
    """
    Add a bold serif title and optional italic subtitle above the axes.
    Returns the title text artist so callers can reposition if needed.
    """
    t = ax.set_title(
        title,
        loc="left",
        fontfamily="serif",
        fontsize=18,
        fontweight="bold",
        color=pal.TEXT_DARK,
        pad=subtitle and 28 or 12,
    )
    if subtitle:
        ax.annotate(
            subtitle,
            xy=(0, 1),
            xycoords="axes fraction",
            xytext=(0, 28),
            textcoords="offset points",
            fontfamily="serif",
            fontstyle="italic",
            fontsize=11,
            color=pal.TEXT_MID,
            va="bottom",
        )
    return t


def add_source(fig, source_text):
    """Add a small source attribution at the bottom-left of the figure."""
    fig.text(
        0.01, 0.01,
        f"Source: {source_text}",
        ha="left", va="bottom",
        fontsize=8,
        fontstyle="italic",
        color=pal.TEXT_MID,
        fontfamily="sans-serif",
    )


def add_branding(fig, text="A16Z"):
    """Add a small brand watermark at the bottom-right of the figure."""
    fig.text(
        0.99, 0.01,
        text,
        ha="right", va="bottom",
        fontsize=9,
        fontweight="bold",
        color=pal.TEXT_LIGHT,
        fontfamily="sans-serif",
    )
