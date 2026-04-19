"""Map example — quitemailingyourself theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../default"))

import json
import map as _src
from chart_library import map_chart, save_png, save_svg

OUT = os.path.dirname(__file__)


_CFG = os.path.join(os.path.dirname(__file__), "map.json")


def make_fig(cfg_path=_CFG):
    with open(cfg_path) as f:
        cfg = json.load(f)
    fig = map_chart(_src._df, **cfg)
    return fig


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "map.png"))
    save_svg(fig, os.path.join(OUT, "map.svg"))
    fig.write_html(os.path.join(OUT, "map.html"))
    print("map.png + map.svg written")
