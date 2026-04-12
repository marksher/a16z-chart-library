"""Map chart example — a16z-news theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import json
import pandas as pd
from chart_library import map_chart, save_png, save_svg

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


_CFG = os.path.join(os.path.dirname(__file__), "map.json")


def make_fig(cfg_path=_CFG):
    with open(cfg_path) as f:
        cfg = json.load(f)
    return map_chart(_df, **cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "map.png"))
    save_svg(fig, os.path.join(OUT, "map.svg"))
    fig.write_html(os.path.join(OUT, "map.html"))
    print("map.png + map.svg written")
