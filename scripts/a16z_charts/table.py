"""
Table chart — styled data table rendered as a matplotlib figure.
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np
from . import palette as pal
from .theme import add_title, add_source, add_branding


def table_chart(
    data,
    columns=None,
    title="",
    subtitle=None,
    source=None,
    color_positive=None,
    color_negative=None,
    pct_columns=None,
    branding=True,
    figsize=(12, 6),
):
    """
    Styled data table as a figure.

    Parameters
    ----------
    data            : pd.DataFrame or dict
    columns         : list of columns to include (default: all)
    color_positive  : list of column names where positive values get green color
    color_negative  : list of column names where negative values get red/maroon
    pct_columns     : list of column names to render with % suffix
    """
    df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data
    if columns:
        df = df[columns]

    color_positive = color_positive or []
    color_negative = color_negative or []
    pct_columns = pct_columns or []

    n_rows, n_cols = df.shape
    row_height = 0.5
    fig_height = max(figsize[1], (n_rows + 2) * row_height)
    fig, ax = plt.subplots(figsize=(figsize[0], fig_height))
    fig.patch.set_facecolor(pal.BACKGROUND)
    ax.set_facecolor(pal.BACKGROUND)
    ax.axis("off")

    # ── Build cell text and colors ──────────────────────────────────────────
    cell_text = []
    cell_colors = []

    for _, row in df.iterrows():
        row_text = []
        row_colors = []
        for col in df.columns:
            val = row[col]
            # Format
            if col in pct_columns and pd.notnull(val):
                text = f"{val:.1f}%"
            elif isinstance(val, float):
                text = f"{val:,.1f}"
            elif isinstance(val, (int, np.integer)):
                text = f"{val:,}"
            else:
                text = str(val)
            row_text.append(text)

            # Cell background color for positive/negative columns
            cell_bg = "white"
            if col in color_positive and pd.notnull(val):
                try:
                    fval = float(val)
                    if fval > 0:
                        cell_bg = "#EAF4EC"  # very light green
                    elif fval < 0:
                        cell_bg = "#F7EDED"  # very light maroon
                except (ValueError, TypeError):
                    pass
            elif col in color_negative and pd.notnull(val):
                try:
                    fval = float(val)
                    if fval < 0:
                        cell_bg = "#F7EDED"
                except (ValueError, TypeError):
                    pass
            row_colors.append(cell_bg)

        cell_text.append(row_text)
        cell_colors.append(row_colors)

    # Alternating row shading
    for r in range(n_rows):
        if r % 2 == 1:
            cell_colors[r] = [
                c if c != "white" else "#F0EBE3"
                for c in cell_colors[r]
            ]

    # ── Draw table ───────────────────────────────────────────────────────────
    tbl = ax.table(
        cellText=cell_text,
        colLabels=list(df.columns),
        cellColours=cell_colors,
        colColours=[pal.NAVY] * n_cols,
        cellLoc="center",
        loc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 1.4)

    # Style header row
    for j in range(n_cols):
        cell = tbl[0, j]
        cell.set_text_props(color="white", fontweight="bold",
                            fontfamily="sans-serif")
        cell.set_edgecolor(pal.NAVY)

    # Style body cells
    for r in range(1, n_rows + 1):
        for j in range(n_cols):
            cell = tbl[r, j]
            cell.set_text_props(color=pal.TEXT_DARK, fontfamily="sans-serif")
            cell.set_edgecolor("#E0DAD0")

    if title:
        add_title(ax, title, subtitle)
    if source:
        add_source(fig, source)
    if branding:
        add_branding(fig)

    fig.tight_layout(pad=1.5)
    return fig, ax
