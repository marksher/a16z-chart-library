"""
Combo chart — dual-axis bar + line (the most common combo in a16z charts).
"""

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import pandas as pd
from . import palette as pal
from .theme import style_axes, add_title, add_source, add_branding


def combo_chart(
    data,
    x,
    bar_y,
    line_y,
    title="",
    subtitle=None,
    source=None,
    bar_label=None,
    line_label=None,
    palette=None,
    branding=True,
    figsize=(10, 6),
    **kwargs,
):
    """
    Dual-axis combo chart: bars on left axis, line on right axis.

    Parameters
    ----------
    data       : pd.DataFrame or dict
    x          : column name for x categories
    bar_y      : column name for bar series (left axis)
    line_y     : column name for line series (right axis)
    bar_label  : legend label for bars (defaults to bar_y)
    line_label : legend label for line (defaults to line_y)
    """
    df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data
    colors = palette or pal.PALETTE
    bar_color = colors[0]
    line_color = colors[1] if len(colors) > 1 else pal.MAROON

    bar_label = bar_label or bar_y
    line_label = line_label or line_y

    fig, ax1 = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(pal.BACKGROUND)

    # ── Bars (left axis) ─────────────────────────────────────────────────────
    ax1.bar(df[x], df[bar_y], color=bar_color, zorder=3, width=0.6)
    ax1.set_ylabel(bar_label, color=bar_color, fontsize=10,
                   fontfamily="sans-serif")
    ax1.tick_params(axis="y", labelcolor=pal.TEXT_MID)

    # ── Line (right axis) ────────────────────────────────────────────────────
    ax2 = ax1.twinx()
    ax2.plot(
        df[x], df[line_y],
        color=line_color, linewidth=2.2, zorder=4,
        marker="o", markersize=5,
        markerfacecolor=line_color, markeredgewidth=0,
    )
    ax2.set_ylabel(line_label, color=line_color, fontsize=10,
                   fontfamily="sans-serif")
    ax2.tick_params(axis="y", labelcolor=pal.TEXT_MID)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_edgecolor(pal.SPINE_COLOR)
    ax2.set_facecolor(pal.BACKGROUND)

    # ── Legend ───────────────────────────────────────────────────────────────
    legend_elements = [
        mpatches.Patch(color=bar_color, label=bar_label),
        mlines.Line2D([0], [0], color=line_color, linewidth=2,
                      marker="o", markersize=5, label=line_label),
    ]
    ax1.legend(
        handles=legend_elements,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        ncol=2, frameon=False,
        fontsize=9, labelcolor=pal.TEXT_MID,
    )

    style_axes(ax1)
    ax1.yaxis.grid(True, color=pal.GRID_COLOR, linewidth=0.6, zorder=0)
    ax2.yaxis.grid(False)

    if title:
        add_title(ax1, title, subtitle)
    if source:
        add_source(fig, source)
    if branding:
        add_branding(fig)

    fig.tight_layout(pad=1.5)
    return fig, ax1, ax2
