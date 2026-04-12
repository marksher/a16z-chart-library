"""Map chart example — care-indeed theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../a16z-news"))

import map as _src
from chart_library import map_chart, save_png, save_svg

OUT = os.path.dirname(__file__)


def make_fig():
    return map_chart(
        _src._df,
        locations="country",
        values="investment_b",
        location_mode="ISO-3",
        title="Global AI Investment",
        subtitle="Venture capital investment in AI companies, 2025 (Billions USD)",
        source="PitchBook",
        theme="care-indeed",
        width=900,
        height=500,
    )


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "map.png"))
    save_svg(fig, os.path.join(OUT, "map.svg"))
    fig.write_html(os.path.join(OUT, "map.html"))
    print("map.png + map.svg written")
