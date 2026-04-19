"""Gauge example — default theme."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))

import json
from chart_library import gauge, save_png, save_svg

OUT = os.path.dirname(__file__)

_CFG = os.path.join(os.path.dirname(__file__), "gauge.json")


def make_fig(cfg_path=_CFG):
    """Return the gauge figure (used in all.html gallery)."""
    with open(cfg_path) as f:
        cfg = json.load(f)
    return gauge(**cfg)


if __name__ == "__main__":
    fig = make_fig()
    save_png(fig, os.path.join(OUT, "gauge.png"))
    save_svg(fig, os.path.join(OUT, "gauge.svg"))
    fig.write_html(os.path.join(OUT, "gauge.html"))
    print("gauge.png + gauge.svg written")
