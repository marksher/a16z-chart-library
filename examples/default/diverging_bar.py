"""Diverging bar chart example — default theme (Plotly defaults)."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../default"))

import json
import diverging_bar as _src
from chart_library import diverging_bar, save_png, save_svg

OUT = os.path.dirname(__file__)


_CFG = os.path.join(os.path.dirname(__file__), "diverging_bar.json")


def make_fig(cfg_path=_CFG):
    with open(cfg_path) as f:
        cfg = json.load(f)
    return diverging_bar(_src._df, **cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "diverging_bar.png"))
    save_svg(fig, os.path.join(OUT, "diverging_bar.svg"))
    fig.write_html(os.path.join(OUT, "diverging_bar.html"))
    print("diverging_bar.png + diverging_bar.svg written")
