"""Pie / donut chart example — care-indeed theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../a16z-news"))

import pie as _src
from chart_library import pie, save_png, save_svg

OUT = os.path.dirname(__file__)


def make_fig():
    return pie(
        _src._df,
        labels="category",
        values="share",
        title="AI Investment by Category",
        subtitle="Percentage of total venture investment, 2025",
        source="PitchBook",
        hole=0.55,
        theme="care-indeed",
        width=700,
        height=520,
    )


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "pie.png"))
    save_svg(fig, os.path.join(OUT, "pie.svg"))
    fig.write_html(os.path.join(OUT, "pie.html"))
    print("pie.png + pie.svg written")
