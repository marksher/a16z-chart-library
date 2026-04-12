"""Sparkline bar example — a16z-news theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import json
from chart_library import sparkline_bar, save_png, save_svg
from sparkline_line import _df

OUT = os.path.dirname(__file__)


_CFG = os.path.join(os.path.dirname(__file__), "sparkline_bar.json")


def make_fig(cfg_path=_CFG):
    with open(cfg_path) as f:
        cfg = json.load(f)
    return sparkline_bar(_df, **cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "sparkline_bar.png"))
    save_svg(fig, os.path.join(OUT, "sparkline_bar.svg"))
    fig.write_html(os.path.join(OUT, "sparkline_bar.html"))
    print("sparkline_bar.png + sparkline_bar.svg written")
