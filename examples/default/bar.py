"""Bar chart example — default theme (Plotly defaults)."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../a16z-news"))

import json
import bar as _src
from chart_library import bar, save_png, save_svg

OUT = os.path.dirname(__file__)


_CFG = os.path.join(os.path.dirname(__file__), "bar.json")


def make_fig(cfg_path=_CFG):
    with open(cfg_path) as f:
        cfg = json.load(f)
    return bar(_src._df2, **cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "bar_stacked.png"))
    save_svg(fig, os.path.join(OUT, "bar_stacked.svg"))
    fig.write_html(os.path.join(OUT, "bar_stacked.html"))
    print("bar_stacked.png + bar_stacked.svg written")
