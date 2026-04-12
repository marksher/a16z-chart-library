"""Table chart example — care-indeed theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../a16z-news"))

import table as _src
from chart_library import table, save_png, save_svg

OUT = os.path.dirname(__file__)


def make_fig():
    return table(
        _src._df,
        title="SaaS AI Feature Pricing & Packaging Shifts",
        subtitle="March 2024 – November 2025",
        source="Public pricing pages",
        highlight_rows=[0, 2, 4],
        theme="care-indeed",
        width=860,
    )


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "table.png"))
    save_svg(fig, os.path.join(OUT, "table.svg"))
    fig.write_html(os.path.join(OUT, "table.html"))
    print("table.png + table.svg written")
