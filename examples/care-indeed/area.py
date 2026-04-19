"""Area chart example — care-indeed theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../default"))

import json
import area as _src
from chart_library import area, save_png, save_svg

OUT = os.path.dirname(__file__)


_CFG = os.path.join(os.path.dirname(__file__), "area.json")


def make_fig(cfg_path=_CFG):
    with open(cfg_path) as f:
        cfg = json.load(f)
    return area(_src._df, **cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "area.png"))
    save_svg(fig, os.path.join(OUT, "area.svg"))
    fig.write_html(os.path.join(OUT, "area.html"))
    print("area.png + area.svg written")
