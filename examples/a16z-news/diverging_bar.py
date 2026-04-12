"""Diverging bar chart example — a16z-news theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import json
import pandas as pd
from chart_library import diverging_bar, save_png, save_svg

OUT = os.path.dirname(__file__)

_df = pd.DataFrame({
    "city": [
        "Denver, CO", "Washington, DC", "Omaha, NE", "Los Angeles, CA",
        "Buffalo, NY", "Albuquerque, NM", "Long Beach, CA", "Atlanta, GA",
        "Baltimore, MD", "Chicago, IL", "Norfolk, VA", "Salt Lake City, UT",
        "Dallas, TX", "Austin, TX", "Memphis, TN", "Louisville, KY",
        "Nashville-Davidson, TN", "San Francisco, CA", "Minneapolis, MN",
        "Detroit, MI", "San Antonio, TX", "Philadelphia, PA", "Lincoln, NE",
        "Chattanooga, TN", "St. Louis, MO", "Arlington, VA", "Richmond, VA",
        "El Paso, TX", "Milwaukee, WI", "Fort Worth, TX", "Little Rock, AR",
    ],
    "pct_change": [
        -42, -31, 11, -44, -48, -20, -21, -25, -60, -18, -27, -47,
        -32, 36, -12, 25, -14, -27, 30, -31, -1, -37, 15, -48,
        -40, -7, -15, -50, -1, 42, 13,
    ],
})


_CFG = os.path.join(os.path.dirname(__file__), "diverging_bar.json")


def make_fig(cfg_path=_CFG):
    with open(cfg_path) as f:
        cfg = json.load(f)
    return diverging_bar(_df, **cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "diverging_bar.png"))
    save_svg(fig, os.path.join(OUT, "diverging_bar.svg"))
    fig.write_html(os.path.join(OUT, "diverging_bar.html"))
    print("diverging_bar.png + diverging_bar.svg written")
