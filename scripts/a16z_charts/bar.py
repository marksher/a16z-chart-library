"""
Bar chart — horizontal and vertical.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from . import palette as pal
from .theme import style_axes, add_title, add_source, add_branding


def bar_chart(
    data,
    x,
    y,
    title="",
    subtitle=None,
    source=None,
    orientation="v",
    palette=None,
    show_values=True,
    branding=True,
    figsize=(10, 6),
    **kwargs,
):
    """
    Bar or column chart.

    Parameters
    ----------
    data        : pd.DataFrame or dict
    x           : column name for categories
    y           : column name (single series) or list of names (grouped)
    orientation : 'v' (vertical columns) or 'h' (horizontal bars)
    show_values : annotate each bar with its value
    """
    df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data
    colors = palette or pal.PALETTE

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(pal.BACKGROUND)

    y_cols = [y] if isinstance(y, str) else list(y)
    n_groups = len(df)
    n_series = len(y_cols)
    bar_width = 0.8 / n_series
    x_pos = np.arange(n_groups)

    for i, col in enumerate(y_cols):
        offset = (i - (n_series - 1) / 2) * bar_width
        vals = df[col].values
        color = colors[i % len(colors)]

        if orientation == "v":
            bars = ax.bar(
                x_pos + offset, vals, width=bar_width * 0.92,
                color=color, zorder=3, **kwargs
            )
            if show_values:
                for bar, v in zip(bars, vals):
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + max(vals) * 0.01,
                        f"{v:,.0f}" if abs(v) >= 10 else f"{v:.1f}",
                        ha="center", va="bottom",
                        fontsize=8, color=pal.TEXT_MID,
                        fontfamily="sans-serif",
                    )
        else:
            bars = ax.barh(
                x_pos + offset, vals, height=bar_width * 0.92,
                color=color, zorder=3, **kwargs
            )
            if show_values:
                for bar, v in zip(bars, vals):
                    ax.text(
                        bar.get_width() + max(vals) * 0.01,
                        bar.get_y() + bar.get_height() / 2,
                        f"{v:,.0f}" if abs(v) >= 10 else f"{v:.1f}",
                        ha="left", va="center",
                        fontsize=8, color=pal.TEXT_MID,
                        fontfamily="sans-serif",
                    )

    if orientation == "v":
        ax.set_xticks(x_pos)
        ax.set_xticklabels(df[x], fontfamily="sans-serif", color=pal.TEXT_MID)
        ax.yaxis.grid(True, color=pal.GRID_COLOR, linewidth=0.6, zorder=0)
        ax.xaxis.grid(False)
    else:
        ax.set_yticks(x_pos)
        ax.set_yticklabels(df[x], fontfamily="sans-serif", color=pal.TEXT_MID)
        ax.xaxis.grid(True, color=pal.GRID_COLOR, linewidth=0.6, zorder=0)
        ax.yaxis.grid(False)

    if n_series > 1:
        patches = [
            mpatches.Patch(color=colors[i % len(colors)], label=col)
            for i, col in enumerate(y_cols)
        ]
        ax.legend(handles=patches, loc="upper center",
                  bbox_to_anchor=(0.5, -0.12), ncol=n_series, frameon=False,
                  fontsize=9, labelcolor=pal.TEXT_MID)

    style_axes(ax)
    if title:
        add_title(ax, title, subtitle)
    if source:
        add_source(fig, source)
    if branding:
        add_branding(fig)

    fig.tight_layout(pad=1.5)
    return fig, ax
