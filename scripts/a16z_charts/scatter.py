"""
Scatter chart — dots, bubbles, and dumbbell/range plots.
"""

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import pandas as pd
import numpy as np
from . import palette as pal
from .theme import style_axes, add_title, add_source, add_branding


def scatter_chart(
    data,
    x,
    y,
    title="",
    subtitle=None,
    source=None,
    size_col=None,
    color_col=None,
    label_col=None,
    dumbbell=False,
    dumbbell_start=None,
    dumbbell_end=None,
    dumbbell_y=None,
    palette=None,
    branding=True,
    figsize=(10, 6),
    **kwargs,
):
    """
    Scatter / bubble / dumbbell chart.

    Standard scatter: pass x, y (and optionally size_col, color_col, label_col).
    Dumbbell:         set dumbbell=True, dumbbell_start, dumbbell_end, dumbbell_y.
    """
    df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data
    colors = palette or pal.PALETTE

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(pal.BACKGROUND)

    if dumbbell:
        # ── Dumbbell / range plot ──
        _dumbbell(ax, df, dumbbell_y, dumbbell_start, dumbbell_end, colors)
    else:
        # ── Standard scatter / bubble ──
        sizes = df[size_col] * 10 if size_col else 60

        if color_col and color_col in df.columns:
            categories = df[color_col].unique()
            for i, cat in enumerate(categories):
                mask = df[color_col] == cat
                ax.scatter(
                    df.loc[mask, x], df.loc[mask, y],
                    s=sizes if not size_col else sizes[mask],
                    color=colors[i % len(colors)],
                    alpha=0.85, zorder=3, label=str(cat), **kwargs,
                )
            ax.legend(
                loc="upper center", bbox_to_anchor=(0.5, -0.12),
                ncol=min(len(categories), 5), frameon=False,
                fontsize=9, labelcolor=pal.TEXT_MID,
            )
        else:
            ax.scatter(
                df[x], df[y],
                s=sizes, color=colors[0],
                alpha=0.85, zorder=3, **kwargs,
            )

        if label_col and label_col in df.columns:
            for _, row in df.iterrows():
                ax.annotate(
                    row[label_col],
                    (row[x], row[y]),
                    xytext=(6, 3), textcoords="offset points",
                    fontsize=8, color=pal.TEXT_MID,
                    fontfamily="sans-serif",
                )

    style_axes(ax)
    if title:
        add_title(ax, title, subtitle)
    if source:
        add_source(fig, source)
    if branding:
        add_branding(fig)

    fig.tight_layout(pad=1.5)
    return fig, ax


def _dumbbell(ax, df, y_col, start_col, end_col, colors):
    """Draw a dumbbell (range) plot on ax."""
    y_pos = range(len(df))
    start_color = colors[0]
    end_color = colors[1] if len(colors) > 1 else colors[0]

    for i, (_, row) in enumerate(df.iterrows()):
        ax.plot(
            [row[start_col], row[end_col]], [i, i],
            color=pal.SPINE_COLOR, linewidth=2.5, solid_capstyle="round", zorder=2,
        )
        ax.scatter(row[start_col], i, color=start_color, s=80, zorder=3)
        ax.scatter(row[end_col], i, color=end_color, s=80, zorder=3)

    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(df[y_col], fontfamily="sans-serif", color=pal.TEXT_MID)
    ax.yaxis.grid(False)
    ax.xaxis.grid(True, color=pal.GRID_COLOR, linewidth=0.6)

    # Legend dots
    legend_elements = [
        mlines.Line2D([0], [0], marker="o", color="w", markerfacecolor=start_color,
                      markersize=8, label=start_col),
        mlines.Line2D([0], [0], marker="o", color="w", markerfacecolor=end_color,
                      markersize=8, label=end_col),
    ]
    ax.legend(
        handles=legend_elements, loc="upper center",
        bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False,
        fontsize=9, labelcolor=pal.TEXT_MID,
    )
