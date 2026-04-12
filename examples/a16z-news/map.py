"""Map chart example — a16z-news theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import pandas as pd
from chart_library import map_chart, save_png

OUT = os.path.dirname(__file__)

_df = pd.DataFrame({
    "country": [
        "USA", "CHN", "GBR", "IND", "DEU",
        "ISR", "FRA", "CAN", "SGP", "AUS",
        "JPN", "KOR", "SWE", "NLD", "BRA",
    ],
    "investment_b": [
        120, 55, 18, 15, 12,
        10,  9,  8,  7,  6,
        5,   4,  4,  3,  3,
    ],
})


def make_fig():
    return map_chart(
        _df,
        locations="country",
        values="investment_b",
        location_mode="ISO-3",
        title="Global AI Investment",
        subtitle="Venture capital investment in AI companies, 2025 (Billions USD)",
        source="PitchBook",
        theme="a16z-news",
        width=900,
        height=500,
    )


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "map.png"))
    fig.write_html(os.path.join(OUT, "map.html"))
    print("map.png written")
