"""
Area chart — stacked or overlapping.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
from . import palette as pal
from .theme import style_axes, add_title, add_source, add_branding


def area_chart(
    data,
    x,
    y,
    title="",
    subtitle=None,
    source=None,
    stacked=True,
    palette=None,
    alpha=0.85,
    branding=True,
    figsize=(10, 6),
    **kwargs,
):
    """
    Area chart.

    Parameters
    ----------
    data    : pd.DataFrame or dict
    x       : column name for x-axis
    y       : column name or list of column names (series to stack/overlay)
    stacked : True = stackplot; False = fill_between each series independently
    alpha   : fill opacity
    """
    df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data
    colors = palette or pal.PALETTE
    y_cols = [y] if isinstance(y, str) else list(y)

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(pal.BACKGROUND)

    series_colors = [colors[i % len(colors)] for i in range(len(y_cols))]

    if stacked:
        ax.stackplot(
            df[x],
            [df[col].values for col in y_cols],
            labels=y_cols,
            colors=series_colors,
            alpha=alpha,
            **kwargs,
        )
    else:
        for i, col in enumerate(y_cols):
            color = series_colors[i]
            ax.fill_between(df[x], df[col], alpha=alpha, color=color, label=col)
            ax.plot(df[x], df[col], color=color, linewidth=1.5)

    if len(y_cols) > 1:
        patches = [
            mpatches.Patch(color=series_colors[i], alpha=alpha, label=col)
            for i, col in enumerate(y_cols)
        ]
        ax.legend(
            handles=patches,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.12),
            ncol=min(len(y_cols), 4),
            frameon=False,
            fontsize=9,
            labelcolor=pal.TEXT_MID,
        )

    if len(df) > 8:
        ax.tick_params(axis="x", rotation=30)

    style_axes(ax)
    if title:
        add_title(ax, title, subtitle)
    if source:
        add_source(fig, source)
    if branding:
        add_branding(fig)

    fig.tight_layout(pad=1.5)
    return fig, ax
