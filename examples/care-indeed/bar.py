"""Bar chart example — care-indeed theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../a16z-news"))

import bar as _src
from chart_library import bar, save_png, save_svg

OUT = os.path.dirname(__file__)


def make_fig():
    return bar(
        _src._df2,
        x="year",
        y=["Microsoft", "Meta", "Alphabet", "Amazon", "Oracle"],
        title="Hyperscaler Capex To The Moon",
        subtitle="Combined capital expenditures expected to top $650 billion in 2026",
        source="Bloomberg",
        stacked=True,
        show_values=False,
        theme="care-indeed",
        width=900,
        height=560,
    )


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "bar_stacked.png"))
    save_svg(fig, os.path.join(OUT, "bar_stacked.svg"))
    fig.write_html(os.path.join(OUT, "bar_stacked.html"))
    print("bar_stacked.png + bar_stacked.svg written")
