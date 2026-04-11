"""
Line chart — multi-series, solid and dashed (for projections).
"""

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import pandas as pd
from . import palette as pal
from .theme import style_axes, add_title, add_source, add_branding


def line_chart(
    data,
    x,
    y,
    title="",
    subtitle=None,
    source=None,
    dashed=None,
    palette=None,
    markers=False,
    branding=True,
    figsize=(10, 6),
    **kwargs,
):
    """
    Line chart.

    Parameters
    ----------
    data    : pd.DataFrame or dict
    x       : column name for x-axis
    y       : column name or list of column names
    dashed  : list of series names to render as dashed (e.g. projections)
    markers : show point markers on lines
    """
    df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data
    colors = palette or pal.PALETTE
    dashed = dashed or []
    y_cols = [y] if isinstance(y, str) else list(y)

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(pal.BACKGROUND)

    for i, col in enumerate(y_cols):
        color = colors[i % len(colors)]
        linestyle = "--" if col in dashed else "-"
        marker = "o" if markers else None
        ax.plot(
            df[x], df[col],
            color=color,
            linestyle=linestyle,
            linewidth=2.2,
            marker=marker,
            markersize=5,
            markerfacecolor=color,
            markeredgewidth=0,
            label=col,
            **kwargs,
        )

    if len(y_cols) > 1:
        handles = []
        for i, col in enumerate(y_cols):
            color = colors[i % len(colors)]
            ls = "--" if col in dashed else "-"
            handles.append(
                mlines.Line2D([], [], color=color, linestyle=ls,
                              linewidth=2, label=col)
            )
        ax.legend(
            handles=handles,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.12),
            ncol=min(len(y_cols), 4),
            frameon=False,
            fontsize=9,
            labelcolor=pal.TEXT_MID,
        )

    # Rotate x-tick labels if there are many
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
