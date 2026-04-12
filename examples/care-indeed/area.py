"""Area chart example — care-indeed theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../a16z-news"))

import area as _src
from chart_library import area, save_png, save_svg

OUT = os.path.dirname(__file__)


def make_fig():
    return area(
        _src._df,
        x="year",
        y=["Permian Basin", "Appalachia", "Haynesville", "Eagle Ford", "Other"],
        title="US Marketable Natural Gas Production by Play",
        subtitle="Bcf/d",
        source="EIA; Wood Mackenzie",
        stacked=True,
        theme="care-indeed",
        width=900,
        height=560,
    )


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "area.png"))
    save_svg(fig, os.path.join(OUT, "area.svg"))
    fig.write_html(os.path.join(OUT, "area.html"))
    print("area.png + area.svg written")
