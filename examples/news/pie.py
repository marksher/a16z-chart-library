"""Pie / donut chart example — default theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import json
import pandas as pd
from chart_library import pie, save_png, save_svg

OUT = os.path.dirname(__file__)

_df = pd.DataFrame({
    "category": [
        "Foundation Models",
        "Developer Tooling",
        "Enterprise AI",
        "Consumer AI",
        "AI Infrastructure",
        "Other",
    ],
    "share": [38, 22, 18, 12, 7, 3],
})


_CFG = os.path.join(os.path.dirname(__file__), "pie.json")


def make_fig(cfg_path=_CFG):
    with open(cfg_path) as f:
        cfg = json.load(f)
    return pie(_df, **cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "pie.png"))
    save_svg(fig, os.path.join(OUT, "pie.svg"))
    fig.write_html(os.path.join(OUT, "pie.html"))
    print("pie.png + pie.svg written")
