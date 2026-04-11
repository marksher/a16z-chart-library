"""
Donut chart — always renders as a donut (not a solid pie), matching a16z style.
"""

import matplotlib.pyplot as plt
import pandas as pd
from . import palette as pal
from .theme import style_axes, add_title, add_source, add_branding


def donut_chart(
    data,
    labels,
    values,
    title="",
    subtitle=None,
    source=None,
    palette=None,
    hole=0.55,
    show_pct=True,
    branding=True,
    figsize=(8, 6),
    **kwargs,
):
    """
    Donut chart.

    Parameters
    ----------
    data       : pd.DataFrame or dict
    labels     : column name for slice labels
    values     : column name for slice sizes
    hole       : radius of center hole (0–1); default 0.55
    show_pct   : annotate each slice with its percentage in matching color
    """
    df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data
    colors = (palette or pal.PALETTE)[:len(df)]

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(pal.BACKGROUND)
    ax.set_facecolor(pal.BACKGROUND)

    wedges, texts = ax.pie(
        df[values],
        labels=None,
        colors=colors,
        startangle=90,
        wedgeprops={"width": 1 - hole, "edgecolor": pal.BACKGROUND, "linewidth": 2},
        **kwargs,
    )

    if show_pct:
        total = df[values].sum()
        for i, (wedge, val) in enumerate(zip(wedges, df[values])):
            pct = val / total * 100
            angle = (wedge.theta1 + wedge.theta2) / 2
            x = (hole + (1 - hole) / 2) * 0.9 * __import__("math").cos(
                __import__("math").radians(angle)
            )
            y = (hole + (1 - hole) / 2) * 0.9 * __import__("math").sin(
                __import__("math").radians(angle)
            )
            ax.text(
                x, y,
                f"{pct:.0f}%",
                ha="center", va="center",
                fontsize=10, fontweight="bold",
                color="white",
                fontfamily="sans-serif",
            )

    # Legend below
    ax.legend(
        wedges, df[labels].tolist(),
        loc="upper center",
        bbox_to_anchor=(0.5, -0.05),
        ncol=min(len(df), 4),
        frameon=False,
        fontsize=9,
        labelcolor=pal.TEXT_MID,
    )

    ax.set_aspect("equal")
    ax.axis("off")

    if title:
        add_title(ax, title, subtitle)
    if source:
        add_source(fig, source)
    if branding:
        add_branding(fig)

    fig.tight_layout(pad=1.5)
    return fig, ax
